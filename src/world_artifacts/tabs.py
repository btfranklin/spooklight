from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from django.urls import reverse

from worlds.models import World
from world_artifacts.models import (
    ImportantEvent,
    StoryConcept,
    WorldCharacter,
    WorldImageReference,
    WorldLocation,
    WorldTruth,
)


@dataclass(frozen=True)
class ArtifactTab:
    key: str
    label: str
    add_label: str
    model: type[Any] | None = None
    queryset_name: str = ""
    create_route: str = ""


ARTIFACT_TABS = [
    ArtifactTab("aesthetics", "Aesthetics", "Edit aesthetics"),
    ArtifactTab(
        "truths",
        "Truths",
        "Add truth",
        model=WorldTruth,
        queryset_name="worldtruths",
        create_route="worlds:world_artifacts:create_truth",
    ),
    ArtifactTab(
        "characters",
        "Characters",
        "Add character",
        model=WorldCharacter,
        queryset_name="worldcharacters",
        create_route="worlds:world_artifacts:create_character",
    ),
    ArtifactTab(
        "locations",
        "Locations",
        "Add location",
        model=WorldLocation,
        queryset_name="worldlocations",
        create_route="worlds:world_artifacts:create_location",
    ),
    ArtifactTab(
        "events",
        "Events",
        "Add event",
        model=ImportantEvent,
        queryset_name="importantevents",
        create_route="worlds:world_artifacts:create_event",
    ),
    ArtifactTab(
        "images",
        "Images",
        "Add image",
        model=WorldImageReference,
        queryset_name="worldimagereferences",
        create_route="worlds:world_artifacts:create_image",
    ),
    ArtifactTab(
        "stories",
        "Stories",
        "Add story",
        model=StoryConcept,
        queryset_name="storyconcepts",
        create_route="worlds:world_artifacts:create_story",
    ),
]

TAB_BY_KEY = {tab.key: tab for tab in ARTIFACT_TABS}
DEFAULT_TAB = "aesthetics"


def normalize_tab_key(tab_key: str | None) -> str:
    if tab_key in TAB_BY_KEY:
        return str(tab_key)
    return DEFAULT_TAB


def build_tab_context(world: World, active_tab_key: str) -> dict[str, Any]:
    active_tab = TAB_BY_KEY[normalize_tab_key(active_tab_key)]
    add_url = reverse(
        "worlds:world_artifacts:edit_aesthetics",
        kwargs={"slug": world.slug},
    )
    items = []

    if active_tab.model is not None:
        items = list(
            active_tab.model.objects.filter(world=world).order_by(
                "-updated_at",
                "title",
            )
        )
        add_url = reverse(active_tab.create_route, kwargs={"slug": world.slug})

    return {
        "artifact_tabs": ARTIFACT_TABS,
        "active_tab": active_tab,
        "active_tab_key": active_tab.key,
        "artifact_items": items,
        "artifact_add_url": add_url,
    }
