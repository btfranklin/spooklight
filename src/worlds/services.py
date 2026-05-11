from __future__ import annotations

import base64
import os

from django.core.files.base import ContentFile
from django.db import transaction
from django.utils.text import slugify
from openai import OpenAI

from worlds.models import World, WorldCoverImage

WORLD_COVER_MODEL = "gpt-image-2"
WORLD_COVER_SIZE = "1536x1024"
WORLD_COVER_QUALITY = "medium"


def build_unique_world_slug(owner_id: int, name: str) -> str:
    base_slug = slugify(name) or "world"
    slug = base_slug
    suffix = 2
    while World.objects.filter(owner_id=owner_id, slug=slug).exists():
        slug = f"{base_slug}-{suffix}"
        suffix += 1
    return slug


def build_world_cover_prompt(world: World) -> str:
    metadata = [
        f"World name: {world.name}",
        f"Genre or archetype: {world.genre or 'not specified'}",
        f"World seed: {world.description or 'not specified'}",
        f"Aesthetic principles: {world.aesthetic_notes or 'not specified'}",
    ]
    return "\n".join(
        [
            "Create a cinematic world cover image for a fictional world dashboard.",
            (
                "The image should feel like a window into the world, "
                "not a generic book cover."
            ),
            "Incorporate the world name into the image as tasteful title art.",
            (
                "Prioritize atmosphere, architecture, materials, lighting, "
                "and visual motifs."
            ),
            (
                "Do not add extra marketing copy, UI chrome, watermarks, logos, "
                "or author names."
            ),
            *metadata,
        ]
    )


def request_world_cover_image(prompt: str) -> bytes:
    if not os.environ.get("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    client = OpenAI()
    result = client.images.generate(
        model=WORLD_COVER_MODEL,
        prompt=prompt,
        size=WORLD_COVER_SIZE,
        quality=WORLD_COVER_QUALITY,
    )
    image_base64 = result.data[0].b64_json
    return base64.b64decode(image_base64)


def generate_cover_image(cover_id: int) -> None:
    cover = WorldCoverImage.objects.select_related("world").get(id=cover_id)
    prompt = cover.prompt or build_world_cover_prompt(cover.world)
    cover.prompt = prompt
    cover.model_id = WORLD_COVER_MODEL
    cover.status = WorldCoverImage.Status.RUNNING
    cover.error_message = ""
    cover.save(
        update_fields=["prompt", "model_id", "status", "error_message", "updated_at"]
    )

    try:
        image_bytes = request_world_cover_image(prompt)
    except Exception as exc:
        cover.status = WorldCoverImage.Status.FAILED
        cover.error_message = str(exc)
        cover.save(update_fields=["status", "error_message", "updated_at"])
        return

    with transaction.atomic():
        cover.image.save(
            f"world-cover-{cover.world_id}.png",
            ContentFile(image_bytes),
            save=False,
        )
        cover.status = WorldCoverImage.Status.SUCCEEDED
        cover.error_message = ""
        cover.is_active = True
        WorldCoverImage.objects.filter(world=cover.world, is_active=True).exclude(
            id=cover.id
        ).update(is_active=False)
        cover.save(
            update_fields=[
                "image",
                "status",
                "error_message",
                "is_active",
                "updated_at",
            ]
        )
