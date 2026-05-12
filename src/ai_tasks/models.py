from __future__ import annotations

import uuid

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone


class AITask(models.Model):
    class Kind(models.TextChoices):
        WORLD_COVER_GENERATION = (
            "world_cover_generation",
            "World cover generation",
        )

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"
        DEAD_LETTERED = "dead_lettered", "Dead lettered"

    TERMINAL_STATUSES = {
        Status.SUCCEEDED,
        Status.FAILED,
        Status.CANCELLED,
        Status.DEAD_LETTERED,
    }

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="ai_tasks",
    )
    world = models.ForeignKey(
        "worlds.World",
        on_delete=models.CASCADE,
        related_name="ai_tasks",
    )
    kind = models.CharField(max_length=80, choices=Kind.choices)
    status = models.CharField(
        max_length=24,
        choices=Status.choices,
        default=Status.QUEUED,
    )
    target_content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    target_object_id = models.CharField(max_length=64, blank=True)
    target = GenericForeignKey("target_content_type", "target_object_id")
    input_payload = models.JSONField(default=dict, blank=True)
    result_payload = models.JSONField(default=dict, blank=True)
    provider = models.CharField(max_length=80, default="openai", blank=True)
    provider_model = models.CharField(max_length=120, blank=True)
    provider_request_id = models.CharField(max_length=200, blank=True)
    queue_job_id = models.CharField(max_length=200, blank=True)
    attempt_count = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=1)
    retry_not_before = models.DateTimeField(null=True, blank=True)
    lease_owner = models.CharField(max_length=160, blank=True)
    leased_at = models.DateTimeField(null=True, blank=True)
    provider_started_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    last_failed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["owner", "status"]),
            models.Index(fields=["world", "status"]),
            models.Index(fields=["kind", "status"]),
            models.Index(fields=["status", "retry_not_before"]),
            models.Index(fields=["status", "leased_at"]),
            models.Index(fields=["target_content_type", "target_object_id"]),
        ]

    def __str__(self) -> str:
        return f"{self.kind}:{self.status}:{self.id}"

    @property
    def is_terminal(self) -> bool:
        return self.status in self.TERMINAL_STATUSES

    @property
    def is_active(self) -> bool:
        return self.status in {self.Status.QUEUED, self.Status.RUNNING}


class AITaskEvent(models.Model):
    task = models.ForeignKey(
        AITask,
        on_delete=models.CASCADE,
        related_name="events",
    )
    sequence = models.PositiveBigIntegerField()
    event_type = models.CharField(max_length=80)
    payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["sequence"]
        constraints = [
            models.UniqueConstraint(
                fields=["task", "sequence"],
                name="unique_ai_task_event_sequence",
            )
        ]

    def __str__(self) -> str:
        return f"{self.task_id}:{self.sequence}:{self.event_type}"


class AIWorkerHeartbeat(models.Model):
    worker_id = models.CharField(max_length=160, primary_key=True)
    queues = models.JSONField(default=list, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    last_seen_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["worker_id"]

    def __str__(self) -> str:
        return self.worker_id
