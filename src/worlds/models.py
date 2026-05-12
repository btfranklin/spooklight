from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils.functional import cached_property


def world_cover_upload_path(instance: WorldCoverImage, filename: str) -> str:
    extension = Path(filename).suffix or ".png"
    return f"world-covers/{instance.world_id}/{uuid4().hex}{extension}"


class World(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="worlds",
    )
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=140)
    description = models.TextField(blank=True)
    genre = models.CharField(max_length=160, blank=True)
    aesthetic_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "slug"],
                name="unique_world_slug_per_owner",
            )
        ]
        indexes = [
            models.Index(fields=["owner", "-updated_at"]),
        ]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("worlds:detail", kwargs={"slug": self.slug})

    @cached_property
    def active_cover(self) -> WorldCoverImage | None:
        return self.cover_images.filter(is_active=True).first()

    @cached_property
    def latest_cover(self) -> WorldCoverImage | None:
        return self.cover_images.first()


class WorldCoverImage(models.Model):
    class Source(models.TextChoices):
        GENERATED = "generated", "Generated"
        UPLOADED = "uploaded", "Uploaded"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        RUNNING = "running", "Running"
        SUCCEEDED = "succeeded", "Succeeded"
        FAILED = "failed", "Failed"

    world = models.ForeignKey(
        World,
        on_delete=models.CASCADE,
        related_name="cover_images",
    )
    ai_task = models.ForeignKey(
        "ai_tasks.AITask",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cover_images",
    )
    image = models.FileField(upload_to=world_cover_upload_path, blank=True)
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.GENERATED,
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    prompt = models.TextField(blank=True)
    model_id = models.CharField(max_length=80, default="gpt-image-2")
    error_message = models.TextField(blank=True)
    is_active = models.BooleanField(default=False)
    generation_task_id = models.CharField(max_length=80, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["world"],
                condition=Q(is_active=True),
                name="unique_active_cover_per_world",
            )
        ]
        indexes = [
            models.Index(fields=["world", "-created_at"]),
            models.Index(fields=["status"]),
            models.Index(fields=["ai_task"]),
        ]

    def __str__(self) -> str:
        return f"{self.world} cover ({self.get_status_display()})"
