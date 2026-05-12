from __future__ import annotations

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError
from django.utils import timezone

from ai_tasks.models import AITask, AIWorkerHeartbeat
from ai_tasks.services import (
    create_ai_task,
    recover_stale_ai_tasks,
    record_task_event,
    succeed_ai_task,
)
from worlds.models import World
from worlds.services import build_unique_world_slug


pytestmark = pytest.mark.django_db


def create_user(username: str):
    from django.contrib.auth import get_user_model

    user_model = get_user_model()
    return user_model.objects.create_user(username=username)


def create_world(owner, name: str = "Riverpunk Delta") -> World:
    return World.objects.create(
        owner=owner,
        name=name,
        slug=build_unique_world_slug(owner.id, name),
    )


def test_ai_task_creation_records_ordered_events() -> None:
    owner = create_user("owner")
    world = create_world(owner)

    task = create_ai_task(
        owner=owner,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
    )
    record_task_event(task, "custom", {"ok": True})

    assert task.status == AITask.Status.QUEUED
    assert list(task.events.values_list("sequence", "event_type")) == [
        (1, "queued"),
        (2, "custom"),
    ]


def test_terminal_task_updates_are_idempotent() -> None:
    owner = create_user("owner")
    world = create_world(owner)
    task = create_ai_task(
        owner=owner,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
    )

    succeed_ai_task(task, result_payload={"first": True})
    succeed_ai_task(task, result_payload={"second": True})
    task.refresh_from_db()

    assert task.status == AITask.Status.SUCCEEDED
    assert task.result_payload == {"first": True}
    assert list(task.events.values_list("event_type", flat=True)) == [
        "queued",
        "succeeded",
    ]


def test_stale_running_task_without_provider_work_is_recovered() -> None:
    owner = create_user("owner")
    world = create_world(owner)
    task = create_ai_task(
        owner=owner,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
        max_attempts=2,
    )
    old_time = timezone.now() - timedelta(hours=1)
    AITask.objects.filter(id=task.id).update(
        status=AITask.Status.RUNNING,
        attempt_count=1,
        leased_at=old_time,
        lease_owner="old-worker",
        queue_job_id="job-1",
    )

    recovered = recover_stale_ai_tasks(requeue=False)
    task.refresh_from_db()

    assert recovered == 1
    assert task.status == AITask.Status.QUEUED
    assert task.queue_job_id == ""
    assert task.events.last().event_type == "recovered"


def test_stale_running_task_after_provider_work_is_dead_lettered() -> None:
    owner = create_user("owner")
    world = create_world(owner)
    task = create_ai_task(
        owner=owner,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
        max_attempts=2,
    )
    old_time = timezone.now() - timedelta(hours=1)
    AITask.objects.filter(id=task.id).update(
        status=AITask.Status.RUNNING,
        attempt_count=1,
        leased_at=old_time,
        lease_owner="old-worker",
        provider_started_at=old_time,
    )

    recovered = recover_stale_ai_tasks(requeue=False)
    task.refresh_from_db()

    assert recovered == 1
    assert task.status == AITask.Status.DEAD_LETTERED
    assert task.events.last().event_type == "dead_lettered"


def test_worker_health_command_requires_fresh_heartbeat() -> None:
    with pytest.raises(CommandError):
        call_command("check_ai_worker_health")

    AIWorkerHeartbeat.objects.create(
        worker_id="worker-1",
        metadata={"state": "stopped"},
    )

    with pytest.raises(CommandError):
        call_command("check_ai_worker_health")

    AIWorkerHeartbeat.objects.create(
        worker_id="worker-2",
        metadata={"state": "idle"},
    )

    call_command("check_ai_worker_health")
