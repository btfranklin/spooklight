from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError

from ai_tasks.models import AIWorkerHeartbeat
from ai_tasks.services import worker_heartbeat_is_fresh


class Command(BaseCommand):
    help = "Check whether an AI background worker heartbeat is fresh."

    def handle(self, *args: str, **options: str) -> None:
        heartbeat = AIWorkerHeartbeat.objects.order_by("-last_seen_at").first()
        if heartbeat is None or not worker_heartbeat_is_fresh():
            raise CommandError("AI worker heartbeat is stale or missing.")
        self.stdout.write(
            self.style.SUCCESS(
                "AI worker heartbeat is healthy "
                f"({heartbeat.worker_id} at {heartbeat.last_seen_at.isoformat()})."
            )
        )
