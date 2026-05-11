from __future__ import annotations

from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from worlds.models import World, WorldCoverImage
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
        genre="Riverpunk",
        aesthetic_notes="Sepia river photography, stilt villages, steam machinery.",
    )


def test_world_slugs_are_unique_per_owner() -> None:
    owner = create_user("owner")
    other_owner = create_user("other-owner")
    first = create_world(owner, "The Salt Moon")
    second_slug = build_unique_world_slug(owner.id, "The Salt Moon")
    other_slug = build_unique_world_slug(other_owner.id, "The Salt Moon")

    assert first.slug == "the-salt-moon"
    assert second_slug == "the-salt-moon-2"
    assert other_slug == "the-salt-moon"


def test_dashboard_shows_empty_state_for_user_without_worlds(client: Client) -> None:
    user = create_user("empty")
    client.force_login(user)

    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert b"Create your first world." in response.content
    assert b"Create world" in response.content


def test_dashboard_renders_owned_world_cards(client: Client) -> None:
    owner = create_user("owner")
    other_owner = create_user("other")
    world = create_world(owner)
    create_world(other_owner, "Other World")
    client.force_login(owner)

    response = client.get(reverse("core:dashboard"))

    assert response.status_code == 200
    assert world.name.encode() in response.content
    assert world.get_absolute_url().encode() in response.content
    assert b"Other World" not in response.content


def test_create_world_post_assigns_owner_and_redirects(client: Client) -> None:
    owner = create_user("creator")
    client.force_login(owner)

    response = client.post(
        reverse("worlds:create"),
        {
            "name": "Brass Marsh",
            "description": "A marsh world of machines and old river gods.",
            "genre": "Riverpunk",
            "aesthetic_notes": "Fog, brass engines, mossy shrines.",
        },
    )

    world = World.objects.get(name="Brass Marsh")
    assert world.owner == owner
    assert response.status_code == 302
    assert response["Location"] == world.get_absolute_url()


def test_world_detail_rejects_other_users_world(client: Client) -> None:
    owner = create_user("owner")
    intruder = create_user("intruder")
    world = create_world(owner)
    client.force_login(intruder)

    response = client.get(world.get_absolute_url())

    assert response.status_code == 404


def test_generate_cover_rejects_other_users_world(client: Client) -> None:
    owner = create_user("owner")
    intruder = create_user("intruder")
    world = create_world(owner)
    client.force_login(intruder)

    response = client.post(
        reverse("worlds:generate_cover", kwargs={"slug": world.slug})
    )

    assert response.status_code == 404
    assert WorldCoverImage.objects.count() == 0


def test_generate_cover_success_marks_active_and_writes_file(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
    settings,
    tmp_path: Path,
) -> None:
    settings.MEDIA_ROOT = tmp_path
    owner = create_user("owner")
    world = create_world(owner)
    client.force_login(owner)

    monkeypatch.setattr(
        "worlds.services.request_world_cover_image",
        lambda prompt: b"generated image bytes",
    )

    response = client.post(
        reverse("worlds:generate_cover", kwargs={"slug": world.slug})
    )

    cover = WorldCoverImage.objects.get(world=world)
    assert response.status_code == 302
    assert response["Location"] == world.get_absolute_url()
    assert cover.status == WorldCoverImage.Status.SUCCEEDED
    assert cover.is_active is True
    assert cover.model_id == "gpt-image-2"
    assert "World name: Riverpunk Delta" in cover.prompt
    assert (tmp_path / cover.image.name).read_bytes() == b"generated image bytes"


def test_generate_cover_failure_stores_error_without_breaking_world(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = create_user("owner")
    world = create_world(owner)
    client.force_login(owner)

    def fail_generation(prompt: str) -> bytes:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    monkeypatch.setattr("worlds.services.request_world_cover_image", fail_generation)

    response = client.post(
        reverse("worlds:generate_cover", kwargs={"slug": world.slug})
    )

    cover = WorldCoverImage.objects.get(world=world)
    assert response.status_code == 302
    assert response["Location"] == world.get_absolute_url()
    assert cover.status == WorldCoverImage.Status.FAILED
    assert cover.is_active is False
    assert cover.error_message == "OPENAI_API_KEY is not configured."

    detail_response = client.get(world.get_absolute_url())
    assert b"Cover: Failed" in detail_response.content
    assert b"OPENAI_API_KEY is not configured." in detail_response.content
