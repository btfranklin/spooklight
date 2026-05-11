from __future__ import annotations

from django.tasks import task

from worlds.services import generate_cover_image


@task
def generate_world_cover(cover_id: int) -> None:
    generate_cover_image(cover_id)
