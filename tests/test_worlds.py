from __future__ import annotations

from pathlib import Path

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from ai_tasks.models import AITask
from ai_tasks.services import create_ai_task, process_ai_task
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


def test_generate_cover_post_enqueues_without_calling_openai(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = create_user("owner")
    world = create_world(owner)
    client.force_login(owner)

    def fail_if_called(prompt: str) -> bytes:
        raise AssertionError("OpenAI should not be called during the request.")

    def fake_enqueue(task: AITask) -> AITask:
        task.queue_job_id = "job-1"
        task.save(update_fields=["queue_job_id", "updated_at"])
        return task

    monkeypatch.setattr("worlds.services.request_world_cover_image", fail_if_called)
    monkeypatch.setattr("worlds.views.enqueue_ai_task", fake_enqueue)

    response = client.post(
        reverse("worlds:generate_cover", kwargs={"slug": world.slug})
    )

    cover = WorldCoverImage.objects.get(world=world)
    task = AITask.objects.get(world=world)
    assert response.status_code == 302
    assert response["Location"] == world.get_absolute_url()
    assert cover.status == WorldCoverImage.Status.PENDING
    assert cover.ai_task == task
    assert task.status == AITask.Status.QUEUED
    assert task.queue_job_id == "job-1"


def test_generate_cover_task_success_marks_active_and_writes_file(
    monkeypatch: pytest.MonkeyPatch,
    settings,
    tmp_path: Path,
) -> None:
    settings.MEDIA_ROOT = tmp_path
    owner = create_user("owner")
    world = create_world(owner)
    cover = WorldCoverImage.objects.create(
        world=world,
        source=WorldCoverImage.Source.GENERATED,
        status=WorldCoverImage.Status.PENDING,
        prompt="World name: Riverpunk Delta",
        model_id="gpt-image-2",
    )
    task = create_ai_task(
        owner=owner,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
        target=cover,
        provider_model="gpt-image-2",
    )
    cover.ai_task = task
    cover.save(update_fields=["ai_task", "updated_at"])

    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setattr(
        "worlds.services.request_world_cover_image",
        lambda prompt: b"generated image bytes",
    )

    process_ai_task(str(task.id))

    cover.refresh_from_db()
    task.refresh_from_db()
    assert cover.status == WorldCoverImage.Status.SUCCEEDED
    assert cover.is_active is True
    assert cover.model_id == "gpt-image-2"
    assert "World name: Riverpunk Delta" in cover.prompt
    assert (tmp_path / cover.image.name).read_bytes() == b"generated image bytes"
    assert task.status == AITask.Status.SUCCEEDED


def test_generate_cover_task_failure_stores_error_without_breaking_world(
    client: Client,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    owner = create_user("owner")
    world = create_world(owner)
    cover = WorldCoverImage.objects.create(
        world=world,
        source=WorldCoverImage.Source.GENERATED,
        status=WorldCoverImage.Status.PENDING,
        prompt="World name: Riverpunk Delta",
        model_id="gpt-image-2",
    )
    task = create_ai_task(
        owner=owner,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
        target=cover,
        provider_model="gpt-image-2",
    )
    cover.ai_task = task
    cover.save(update_fields=["ai_task", "updated_at"])
    client.force_login(owner)

    def fail_generation(prompt: str) -> bytes:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setattr("worlds.services.request_world_cover_image", fail_generation)

    process_ai_task(str(task.id))

    cover.refresh_from_db()
    task.refresh_from_db()
    assert cover.status == WorldCoverImage.Status.FAILED
    assert cover.is_active is False
    assert cover.error_message == "OPENAI_API_KEY is not configured."
    assert task.status == AITask.Status.FAILED
    assert task.error_message == "OPENAI_API_KEY is not configured."
    assert task.provider_started_at is None

    detail_response = client.get(world.get_absolute_url())
    assert b"OPENAI_API_KEY is not configured." in detail_response.content


def test_world_detail_renders_artifact_tabs_and_empty_add_button(
    client: Client,
) -> None:
    owner = create_user("owner")
    world = create_world(owner)
    client.force_login(owner)

    response = client.get(f"{world.get_absolute_url()}?tab=truths")

    assert response.status_code == 200
    labels = [
        "Aesthetics",
        "Truths",
        "Characters",
        "Locations",
        "Events",
        "Images",
        "Stories",
    ]
    for label in labels:
        assert label.encode() in response.content
    assert b'aria-label="Add truth"' in response.content
    assert (
        b'aria-current="page" class="tab tab-active text-sm font-semibold">Truths'
        in response.content
    )
