from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from django.db import models


def reference_image_upload_path(instance: WorldImageReference, filename: str) -> str:
    extension = Path(filename).suffix or ".png"
    return f"world-references/{instance.world_id}/{uuid4().hex}{extension}"


class WorldArtifactBase(models.Model):
    world = models.ForeignKey(
        "worlds.World",
        on_delete=models.CASCADE,
        related_name="%(class)ss",
    )
    title = models.CharField(max_length=160)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class WorldTruth(WorldArtifactBase):
    text = models.TextField()

    class Meta(WorldArtifactBase.Meta):
        indexes = [models.Index(fields=["world", "title"])]


class WorldCharacter(WorldArtifactBase):
    role = models.CharField(max_length=160, blank=True)
    appearance = models.TextField(blank=True)
    personality = models.TextField(blank=True)
    motivations = models.TextField(blank=True)
    current_status = models.CharField(max_length=160, blank=True)

    class Meta(WorldArtifactBase.Meta):
        indexes = [models.Index(fields=["world", "title"])]


class WorldLocation(WorldArtifactBase):
    location_type = models.CharField(max_length=120, blank=True)
    geography = models.TextField(blank=True)
    visual_character = models.TextField(blank=True)
    significance = models.TextField(blank=True)

    class Meta(WorldArtifactBase.Meta):
        indexes = [models.Index(fields=["world", "title"])]


class ImportantEvent(WorldArtifactBase):
    class EventState(models.TextChoices):
        HISTORICAL = "historical", "Historical"
        CURRENT = "current", "Current"
        PREDICTED = "predicted", "Predicted"
        MYTHIC = "mythic", "Mythic"
        DISPUTED = "disputed", "Disputed"

    time_period = models.CharField(max_length=160, blank=True)
    event_state = models.CharField(
        max_length=20,
        choices=EventState.choices,
        default=EventState.HISTORICAL,
    )
    participants = models.TextField(blank=True)
    causes = models.TextField(blank=True)
    consequences = models.TextField(blank=True)

    class Meta(WorldArtifactBase.Meta):
        indexes = [models.Index(fields=["world", "title"])]


class WorldImageReference(WorldArtifactBase):
    class Source(models.TextChoices):
        GENERATED = "generated", "Generated"
        UPLOADED = "uploaded", "Uploaded"

    class Role(models.TextChoices):
        INSPIRATION = "inspiration", "Inspiration"
        LITERAL = "literal", "Literal"
        CONCEPT = "concept", "Concept"

    image = models.FileField(upload_to=reference_image_upload_path, blank=True)
    source = models.CharField(
        max_length=20,
        choices=Source.choices,
        default=Source.UPLOADED,
    )
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.INSPIRATION,
    )
    description = models.TextField(blank=True)

    class Meta(WorldArtifactBase.Meta):
        indexes = [models.Index(fields=["world", "title"])]


class StoryConcept(WorldArtifactBase):
    seed = models.TextField(blank=True)
    premise = models.TextField(blank=True)

    class Meta(WorldArtifactBase.Meta):
        indexes = [models.Index(fields=["world", "title"])]
