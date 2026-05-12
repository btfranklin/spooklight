from __future__ import annotations

from django.tasks import task

from ai_tasks.services import process_ai_task


@task(queue_name="ai")
def process_ai_task_task(task_id: str) -> None:
    process_ai_task(task_id)
