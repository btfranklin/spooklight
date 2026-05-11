from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from worlds.forms import WorldForm
from worlds.models import World, WorldCoverImage
from worlds.services import build_unique_world_slug, build_world_cover_prompt
from worlds.tasks import generate_world_cover


def get_owned_world(request: HttpRequest, slug: str) -> World:
    return get_object_or_404(World, owner=request.user, slug=slug)


@login_required
def create_world(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = WorldForm(request.POST)
        if form.is_valid():
            world = form.save(commit=False)
            world.owner = request.user
            world.slug = build_unique_world_slug(request.user.id, world.name)
            world.save()
            messages.success(request, "World created.")
            return redirect(world)
    else:
        form = WorldForm()

    return render(request, "worlds/world_form.html", {"form": form})


@login_required
def world_detail(request: HttpRequest, slug: str) -> HttpResponse:
    world = get_owned_world(request, slug)
    return render(request, "worlds/world_detail.html", {"world": world})


@login_required
@require_POST
def generate_cover(request: HttpRequest, slug: str) -> HttpResponse:
    world = get_owned_world(request, slug)
    cover = WorldCoverImage.objects.create(
        world=world,
        source=WorldCoverImage.Source.GENERATED,
        status=WorldCoverImage.Status.PENDING,
        prompt=build_world_cover_prompt(world),
        model_id="gpt-image-2",
    )
    task_result = generate_world_cover.enqueue(cover.id)
    cover.generation_task_id = task_result.id
    cover.save(update_fields=["generation_task_id", "updated_at"])

    cover.refresh_from_db()
    if cover.status == WorldCoverImage.Status.FAILED:
        messages.error(request, f"Cover generation failed: {cover.error_message}")
    elif cover.status == WorldCoverImage.Status.SUCCEEDED:
        messages.success(request, "Cover image generated.")
    else:
        messages.info(request, "Cover image generation started.")

    return redirect(world)
