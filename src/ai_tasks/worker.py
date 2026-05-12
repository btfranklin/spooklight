from __future__ import annotations

import contextlib

from django.db import close_old_connections
from rq import Worker

from ai_tasks.services import record_worker_heartbeat


class TrackedWorker(Worker):
    def heartbeat(self, timeout=None, pipeline=None):  # type: ignore[no-untyped-def]
        result = super().heartbeat(timeout=timeout, pipeline=pipeline)
        self._record_ai_heartbeat()
        return result

    def register_birth(self):  # type: ignore[no-untyped-def]
        result = super().register_birth()
        self._record_ai_heartbeat()
        return result

    def register_death(self):  # type: ignore[no-untyped-def]
        result = super().register_death()
        self._record_ai_heartbeat(metadata={"state": "stopped"})
        return result

    def _record_ai_heartbeat(self, *, metadata=None) -> None:  # type: ignore[no-untyped-def]
        close_old_connections()
        with contextlib.suppress(Exception):
            record_worker_heartbeat(
                worker_id=str(self.name),
                queues=[queue.name for queue in self.queues],
                metadata=metadata or {"state": str(self.get_state())},
            )
