from __future__ import annotations

from django.contrib import admin

from world_artifacts.models import (
    ImportantEvent,
    StoryConcept,
    WorldCharacter,
    WorldImageReference,
    WorldLocation,
    WorldTruth,
)


for model in (
    WorldTruth,
    WorldCharacter,
    WorldLocation,
    ImportantEvent,
    WorldImageReference,
    StoryConcept,
):
    admin.site.register(model)
