from __future__ import annotations

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from world_artifacts.models import (
    ImportantEvent,
    StoryConcept,
    WorldCharacter,
    WorldImageReference,
    WorldLocation,
    WorldTruth,
)
from worlds.models import World
from worlds.services import build_unique_world_slug


pytestmark = pytest.mark.django_db


def create_user(username: str):
    user_model = get_user_model()
    return user_model.objects.create_user(username=username)


def create_world(owner, name: str = "Riverpunk Delta") -> World:
    return World.objects.create(
        owner=owner,
        name=name,
        slug=build_unique_world_slug(owner.id, name),
        description="A flooded frontier of steamships and temple towns.",
    )


def test_aesthetics_edit_updates_owned_world(client: Client) -> None:
    owner = create_user("owner")
    world = create_world(owner)
    client.force_login(owner)

    response = client.post(
        reverse("worlds:world_artifacts:edit_aesthetics", kwargs={"slug": world.slug}),
        {
            "genre": "Riverpunk",
            "aesthetic_notes": "Sepia waterlines and brass engines.",
        },
    )

    world.refresh_from_db()
    assert response.status_code == 302
    assert world.genre == "Riverpunk"
    assert world.aesthetic_notes == "Sepia waterlines and brass engines."


def test_artifact_create_routes_create_owned_world_artifacts(client: Client) -> None:
    owner = create_user("owner")
    world = create_world(owner)
    client.force_login(owner)

    cases = [
        (
            "worlds:world_artifacts:create_truth",
            {"title": "River law", "text": "All debts are witnessed by river stones."},
            WorldTruth,
        ),
        (
            "worlds:world_artifacts:create_character",
            {"title": "Mara Venn", "role": "Pilot"},
            WorldCharacter,
        ),
        (
            "worlds:world_artifacts:create_location",
            {"title": "Siltmarket", "location_type": "Stilt town"},
            WorldLocation,
        ),
        (
            "worlds:world_artifacts:create_event",
            {"title": "The Low Flood", "event_state": "historical"},
            ImportantEvent,
        ),
        (
            "worlds:world_artifacts:create_image",
            {"title": "Temple reference", "source": "uploaded", "role": "inspiration"},
            WorldImageReference,
        ),
        (
            "worlds:world_artifacts:create_story",
            {"title": "The Brass Ferry", "premise": "A ferry carries a forbidden map."},
            StoryConcept,
        ),
    ]

    for route_name, payload, model in cases:
        response = client.post(
            reverse(route_name, kwargs={"slug": world.slug}),
            payload,
        )
        assert response.status_code == 302
        assert model.objects.filter(world=world, title=payload["title"]).exists()


def test_artifact_create_rejects_other_users_world(client: Client) -> None:
    owner = create_user("owner")
    intruder = create_user("intruder")
    world = create_world(owner)
    client.force_login(intruder)

    response = client.post(
        reverse("worlds:world_artifacts:create_truth", kwargs={"slug": world.slug}),
        {"title": "Hidden truth", "text": "Nope."},
    )

    assert response.status_code == 404
    assert WorldTruth.objects.count() == 0
