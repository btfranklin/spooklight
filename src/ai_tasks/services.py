from __future__ import annotations

from datetime import timedelta
import logging
import os
from typing import Any

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Max, Q
from django.utils import timezone

from ai_tasks.models import AITask, AITaskEvent, AIWorkerHeartbeat

logger = logging.getLogger(__name__)


class UnknownAITaskKind(RuntimeError):
    pass


def create_ai_task(
    *,
    owner: Any,
    world: Any,
    kind: str,
    target: Any | None = None,
    input_payload: dict[str, Any] | None = None,
    provider: str = "openai",
    provider_model: str = "",
    max_attempts: int = 1,
) -> AITask:
    content_type = None
    object_id = ""
    if target is not None:
        content_type = ContentType.objects.get_for_model(
            target,
            for_concrete_model=False,
        )
        object_id = str(target.pk)

    task = AITask.objects.create(
        owner=owner,
        world=world,
        kind=kind,
        target_content_type=content_type,
        target_object_id=object_id,
        input_payload=input_payload or {},
        provider=provider,
        provider_model=provider_model,
        max_attempts=max_attempts,
    )
    record_task_event(task, "queued", {"kind": kind})
    return task


def enqueue_ai_task(task: AITask) -> AITask:
    if task.is_terminal:
        return task

    try:
        from ai_tasks.tasks import process_ai_task_task

        task_result = process_ai_task_task.enqueue(str(task.id))
    except Exception as exc:  # noqa: BLE001
        logger.exception(
            "Failed to enqueue AI task",
            extra={"ai_task_id": str(task.id)},
        )
        return fail_ai_task(task, f"Task queue unavailable: {exc}")

    queue_job_id = str(getattr(task_result, "id", "") or "")
    AITask.objects.filter(id=task.id).update(
        queue_job_id=queue_job_id,
        updated_at=timezone.now(),
    )
    task.refresh_from_db()
    record_task_event(task, "enqueued", {"queue_job_id": queue_job_id})
    return task


def process_ai_task(task_id: str) -> None:
    task = claim_ai_task(task_id)
    if task is None:
        return

    try:
        if task.kind == AITask.Kind.WORLD_COVER_GENERATION:
            from worlds.services import process_world_cover_generation_task

            process_world_cover_generation_task(task)
        else:
            raise UnknownAITaskKind(f"Unknown AI task kind: {task.kind}")
    except Exception as exc:  # noqa: BLE001
        logger.exception("AI task failed", extra={"ai_task_id": str(task_id)})
        handle_ai_task_exception(task, exc)
        return

    task.refresh_from_db()
    if not task.is_terminal:
        succeed_ai_task(task)


def claim_ai_task(task_id: str) -> AITask | None:
    now = timezone.now()
    with transaction.atomic():
        task = AITask.objects.select_for_update().filter(id=task_id).first()
        if task is None or task.is_terminal or task.status != AITask.Status.QUEUED:
            return None
        if task.retry_not_before and task.retry_not_before > now:
            return None
        task.status = AITask.Status.RUNNING
        task.attempt_count += 1
        task.started_at = task.started_at or now
        task.lease_owner = _lease_owner()
        task.leased_at = now
        task.error_message = ""
        task.save(
            update_fields=[
                "status",
                "attempt_count",
                "started_at",
                "lease_owner",
                "leased_at",
                "error_message",
                "updated_at",
            ]
        )
    record_task_event(
        task,
        "claimed",
        {"attempt_count": task.attempt_count, "lease_owner": task.lease_owner},
    )
    return task


def mark_provider_started(
    task: AITask,
    *,
    provider_model: str = "",
    provider_request_id: str = "",
) -> AITask:
    if task.is_terminal:
        return task
    task.provider_started_at = timezone.now()
    if provider_model:
        task.provider_model = provider_model
    if provider_request_id:
        task.provider_request_id = provider_request_id
    task.save(
        update_fields=[
            "provider_started_at",
            "provider_model",
            "provider_request_id",
            "updated_at",
        ]
    )
    record_task_event(
        task,
        "provider_started",
        {
            "provider": task.provider,
            "provider_model": task.provider_model,
            "provider_request_id": task.provider_request_id,
        },
    )
    return task


def succeed_ai_task(
    task: AITask,
    *,
    result_payload: dict[str, Any] | None = None,
) -> AITask:
    with transaction.atomic():
        locked = AITask.objects.select_for_update().get(id=task.id)
        if locked.is_terminal:
            return locked
        locked.status = AITask.Status.SUCCEEDED
        locked.result_payload = result_payload or locked.result_payload
        locked.error_message = ""
        locked.lease_owner = ""
        locked.leased_at = None
        locked.finished_at = timezone.now()
        locked.save(
            update_fields=[
                "status",
                "result_payload",
                "error_message",
                "lease_owner",
                "leased_at",
                "finished_at",
                "updated_at",
            ]
        )
    record_task_event(locked, "succeeded", locked.result_payload)
    return locked


def fail_ai_task(task: AITask, error_message: str) -> AITask:
    return _finish_unsuccessfully(
        task,
        status=AITask.Status.FAILED,
        event_type="failed",
        error_message=error_message,
    )


def dead_letter_ai_task(task: AITask, error_message: str) -> AITask:
    return _finish_unsuccessfully(
        task,
        status=AITask.Status.DEAD_LETTERED,
        event_type="dead_lettered",
        error_message=error_message,
    )


def handle_ai_task_exception(task: AITask, exc: Exception) -> AITask:
    task.refresh_from_db()
    if task.provider_started_at is not None or task.attempt_count >= task.max_attempts:
        return fail_ai_task(task, str(exc))

    retry_at = timezone.now() + timedelta(
        seconds=int(getattr(settings, "AI_TASK_RETRY_DELAY_SECONDS", 30))
    )
    with transaction.atomic():
        locked = AITask.objects.select_for_update().get(id=task.id)
        if locked.is_terminal:
            return locked
        locked.status = AITask.Status.QUEUED
        locked.error_message = str(exc)
        locked.last_failed_at = timezone.now()
        locked.retry_not_before = retry_at
        locked.lease_owner = ""
        locked.leased_at = None
        locked.queue_job_id = ""
        locked.save(
            update_fields=[
                "status",
                "error_message",
                "last_failed_at",
                "retry_not_before",
                "lease_owner",
                "leased_at",
                "queue_job_id",
                "updated_at",
            ]
        )
    record_task_event(
        locked,
        "retry_scheduled",
        {
            "error": locked.error_message,
            "attempt_count": locked.attempt_count,
            "retry_not_before": retry_at.isoformat(),
        },
    )
    return enqueue_ai_task(locked)


def recover_stale_ai_tasks(*, requeue: bool = True) -> int:
    now = timezone.now()
    cutoff = now - timedelta(
        seconds=int(getattr(settings, "AI_TASK_LEASE_SECONDS", 900))
    )
    stale = AITask.objects.filter(status=AITask.Status.RUNNING).filter(
        Q(leased_at__isnull=True) | Q(leased_at__lte=cutoff)
    )

    recovered_ids: list[str] = []
    count = 0
    with transaction.atomic():
        for task in stale.select_for_update().order_by("started_at", "created_at"):
            if (
                task.provider_started_at is not None
                or task.attempt_count >= task.max_attempts
            ):
                task.status = AITask.Status.DEAD_LETTERED
                task.error_message = "Task lease expired."
                task.last_failed_at = now
                task.finished_at = now
                task.lease_owner = ""
                task.leased_at = None
                task.save(
                    update_fields=[
                        "status",
                        "error_message",
                        "last_failed_at",
                        "finished_at",
                        "lease_owner",
                        "leased_at",
                        "updated_at",
                    ]
                )
                event_type = "dead_lettered"
                payload = {"reason": "lease_expired"}
            else:
                task.status = AITask.Status.QUEUED
                task.error_message = ""
                task.retry_not_before = None
                task.lease_owner = ""
                task.leased_at = None
                task.queue_job_id = ""
                task.save(
                    update_fields=[
                        "status",
                        "error_message",
                        "retry_not_before",
                        "lease_owner",
                        "leased_at",
                        "queue_job_id",
                        "updated_at",
                    ]
                )
                recovered_ids.append(str(task.id))
                event_type = "recovered"
                payload = {"reason": "lease_expired"}
            _record_task_event_locked(task, event_type, payload)
            count += 1

    if requeue:
        for task in AITask.objects.filter(id__in=recovered_ids):
            enqueue_ai_task(task)

    return count


def enqueue_unqueued_ai_tasks() -> int:
    now = timezone.now()
    queryset = AITask.objects.filter(
        status=AITask.Status.QUEUED,
        queue_job_id="",
    ).filter(Q(retry_not_before__isnull=True) | Q(retry_not_before__lte=now))
    count = 0
    for task in queryset.order_by("created_at"):
        enqueue_ai_task(task)
        count += 1
    return count


def record_task_event(
    task: AITask,
    event_type: str,
    payload: dict[str, Any] | None = None,
) -> AITaskEvent:
    with transaction.atomic():
        locked = AITask.objects.select_for_update().get(id=task.id)
        return _record_task_event_locked(locked, event_type, payload or {})


def record_worker_heartbeat(
    *,
    worker_id: str,
    queues: list[str] | None = None,
    metadata: dict[str, Any] | None = None,
) -> AIWorkerHeartbeat:
    heartbeat, _ = AIWorkerHeartbeat.objects.update_or_create(
        worker_id=worker_id,
        defaults={
            "queues": queues or [],
            "metadata": metadata or {},
            "last_seen_at": timezone.now(),
        },
    )
    return heartbeat


def worker_heartbeat_is_fresh() -> bool:
    cutoff = timezone.now() - timedelta(
        seconds=int(getattr(settings, "AI_WORKER_HEARTBEAT_MAX_AGE_SECONDS", 120))
    )
    return (
        AIWorkerHeartbeat.objects.filter(last_seen_at__gte=cutoff)
        .exclude(metadata__state="stopped")
        .exists()
    )


def _finish_unsuccessfully(
    task: AITask,
    *,
    status: str,
    event_type: str,
    error_message: str,
) -> AITask:
    now = timezone.now()
    with transaction.atomic():
        locked = AITask.objects.select_for_update().get(id=task.id)
        if locked.is_terminal:
            return locked
        locked.status = status
        locked.error_message = error_message
        locked.last_failed_at = now
        locked.finished_at = now
        locked.lease_owner = ""
        locked.leased_at = None
        locked.save(
            update_fields=[
                "status",
                "error_message",
                "last_failed_at",
                "finished_at",
                "lease_owner",
                "leased_at",
                "updated_at",
            ]
        )
    record_task_event(locked, event_type, {"error": error_message})
    return locked


def _record_task_event_locked(
    task: AITask,
    event_type: str,
    payload: dict[str, Any],
) -> AITaskEvent:
    next_sequence = (
        AITaskEvent.objects.filter(task=task)
        .aggregate(max_sequence=Max("sequence"))
        .get("max_sequence")
        or 0
    ) + 1
    return AITaskEvent.objects.create(
        task=task,
        sequence=next_sequence,
        event_type=event_type,
        payload=payload,
    )


def _lease_owner() -> str:
    return f"{os.environ.get('HOSTNAME', 'local')}:{os.getpid()}"
