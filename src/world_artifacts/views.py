from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from worlds.models import World
from world_artifacts.forms import (
    ImportantEventForm,
    StoryConceptForm,
    WorldAestheticsForm,
    WorldCharacterForm,
    WorldImageReferenceForm,
    WorldLocationForm,
    WorldTruthForm,
)
from world_artifacts.tabs import DEFAULT_TAB


def get_owned_world(request: HttpRequest, slug: str) -> World:
    return get_object_or_404(World, owner=request.user, slug=slug)


@login_required
def edit_aesthetics(request: HttpRequest, slug: str) -> HttpResponse:
    world = get_owned_world(request, slug)
    if request.method == "POST":
        form = WorldAestheticsForm(request.POST, instance=world)
        if form.is_valid():
            form.save()
            messages.success(request, "Aesthetics saved.")
            return redirect(f"{world.get_absolute_url()}?tab=aesthetics")
    else:
        form = WorldAestheticsForm(instance=world)
    return render(
        request,
        "world_artifacts/artifact_form.html",
        {
            "world": world,
            "form": form,
            "form_title": "Aesthetics",
            "cancel_url": f"{world.get_absolute_url()}?tab={DEFAULT_TAB}",
        },
    )


@login_required
def create_truth(request: HttpRequest, slug: str) -> HttpResponse:
    return create_artifact(
        request,
        slug,
        form_class=WorldTruthForm,
        form_title="Truth",
        tab_key="truths",
    )


@login_required
def create_character(request: HttpRequest, slug: str) -> HttpResponse:
    return create_artifact(
        request,
        slug,
        form_class=WorldCharacterForm,
        form_title="Character",
        tab_key="characters",
    )


@login_required
def create_location(request: HttpRequest, slug: str) -> HttpResponse:
    return create_artifact(
        request,
        slug,
        form_class=WorldLocationForm,
        form_title="Location",
        tab_key="locations",
    )


@login_required
def create_event(request: HttpRequest, slug: str) -> HttpResponse:
    return create_artifact(
        request,
        slug,
        form_class=ImportantEventForm,
        form_title="Event",
        tab_key="events",
    )


@login_required
def create_image(request: HttpRequest, slug: str) -> HttpResponse:
    return create_artifact(
        request,
        slug,
        form_class=WorldImageReferenceForm,
        form_title="Image",
        tab_key="images",
        include_files=True,
    )


@login_required
def create_story(request: HttpRequest, slug: str) -> HttpResponse:
    return create_artifact(
        request,
        slug,
        form_class=StoryConceptForm,
        form_title="Story",
        tab_key="stories",
    )


def create_artifact(
    request: HttpRequest,
    slug: str,
    *,
    form_class: type,
    form_title: str,
    tab_key: str,
    include_files: bool = False,
) -> HttpResponse:
    world = get_owned_world(request, slug)
    data = request.POST or None
    files = request.FILES if include_files else None
    if request.method == "POST":
        form = form_class(data, files)
        if form.is_valid():
            artifact = form.save(commit=False)
            artifact.world = world
            artifact.save()
            messages.success(request, f"{form_title} saved.")
            return redirect(f"{world.get_absolute_url()}?tab={tab_key}")
    else:
        form = form_class()

    return render(
        request,
        "world_artifacts/artifact_form.html",
        {
            "world": world,
            "form": form,
            "form_title": form_title,
            "cancel_url": f"{world.get_absolute_url()}?tab={tab_key}",
        },
    )
