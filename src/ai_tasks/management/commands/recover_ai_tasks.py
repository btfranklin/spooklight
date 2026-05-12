from __future__ import annotations

from django.core.management.base import BaseCommand

from ai_tasks.services import enqueue_unqueued_ai_tasks, recover_stale_ai_tasks


class Command(BaseCommand):
    help = "Recover stale AI tasks and enqueue queued tasks missing queue jobs."

    def handle(self, *args: str, **options: str) -> None:
        recovered = recover_stale_ai_tasks()
        enqueued = enqueue_unqueued_ai_tasks()
        self.stdout.write(
            self.style.SUCCESS(
                f"Recovered {recovered} stale AI tasks and enqueued "
                f"{enqueued} queued tasks."
            )
        )
