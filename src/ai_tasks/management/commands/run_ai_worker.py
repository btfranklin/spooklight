from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import BaseCommand

from ai_tasks.services import enqueue_unqueued_ai_tasks, recover_stale_ai_tasks


class Command(BaseCommand):
    help = "Run the AI task RQ worker with Spooklight task recovery."

    def handle(self, *args: str, **options: str) -> None:
        recover_stale_ai_tasks()
        enqueue_unqueued_ai_tasks()
        call_command(
            "rqworker",
            "ai",
            "--job-class",
            "django_tasks_rq.Job",
            "--worker-class",
            "ai_tasks.worker.TrackedWorker",
        )
