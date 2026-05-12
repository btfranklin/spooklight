from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django_htmx.http import HttpResponseStopPolling
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST

from ai_tasks.models import AITask
from ai_tasks.services import create_ai_task, enqueue_ai_task
from worlds.forms import WorldForm
from worlds.models import World, WorldCoverImage
from worlds.services import build_unique_world_slug, build_world_cover_prompt
from world_artifacts.tabs import build_tab_context, normalize_tab_key


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
    active_tab_key = normalize_tab_key(request.GET.get("tab"))
    context = {"world": world, **build_tab_context(world, active_tab_key)}
    if request.htmx and request.GET.get("fragment") == "tabs":
        return render(request, "worlds/partials/artifact_tabs.html", context)
    return render(request, "worlds/world_detail.html", context)


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
    ai_task = create_ai_task(
        owner=request.user,
        world=world,
        kind=AITask.Kind.WORLD_COVER_GENERATION,
        target=cover,
        input_payload={"prompt": cover.prompt, "cover_id": cover.id},
        provider_model="gpt-image-2",
        max_attempts=2,
    )
    cover.ai_task = ai_task
    cover.save(update_fields=["ai_task", "updated_at"])
    ai_task = enqueue_ai_task(ai_task)
    cover.generation_task_id = ai_task.queue_job_id
    cover.save(update_fields=["generation_task_id", "updated_at"])

    if ai_task.status == AITask.Status.FAILED:
        messages.error(request, ai_task.error_message)
    else:
        messages.info(request, "Cover generation started.")

    return redirect(world)


@login_required
def cover_status_fragment(request: HttpRequest, slug: str) -> HttpResponse:
    world = get_owned_world(request, slug)
    html = render_to_string(
        "worlds/partials/cover_status.html",
        {"world": world},
        request=request,
    )
    latest_cover = world.latest_cover
    latest_task = latest_cover.ai_task if latest_cover else None
    if request.htmx and latest_task and latest_task.is_terminal:
        return HttpResponseStopPolling(html)
    return HttpResponse(html)
