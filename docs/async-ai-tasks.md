# Async AI Tasks

Spooklight tracks AI work in Postgres first. Redis/RQ is only the execution
transport.

## Source Of Truth

`ai_tasks.AITask` is the authoritative record for every AI operation.
Templates, status fragments, retries, recovery, and support/debugging should
read from `AITask`, not from RQ job state.

`AITaskEvent` records ordered lifecycle events for each task. Use events for
debugging and audit trails, not as the primary status field.

`AIWorkerHeartbeat` records worker liveness for health checks. A fresh stopped
heartbeat is not healthy.

## Lifecycle

Valid statuses are:

- `queued`
- `running`
- `succeeded`
- `failed`
- `cancelled`
- `dead_lettered`

Create tasks through `ai_tasks.services.create_ai_task`, enqueue them through
`enqueue_ai_task`, and execute them through `process_ai_task`. Request handlers
must not call OpenAI directly.

Provider calls should mark `provider_started_at` before the external request.
Once provider work begins, automatic retries are disabled for image generation
so a recovery path does not accidentally duplicate billed image attempts.

## Recovery

`recover_ai_tasks` handles stale running rows:

- Running tasks with no provider work may be returned to `queued`.
- Running tasks with provider work already started are moved to
  `dead_lettered`.

The worker entrypoint runs recovery before starting the RQ worker.

## UI Contract

AI task UI should be driven by owner-scoped fragments. While a task is `queued`
or `running`, render a small spinner and poll. Stop polling when the task enters
a terminal status.

Keep task UI copy minimal. Do not add badges or explanatory panels unless the
user specifically requests them.

## Future Agents SDK Work

`agentic-django` can be introduced later for richer Agents SDK sessions, runs,
and events. If that happens, keep `AITask` as the product-level ledger and link
provider/session records back to the relevant `AITask`.
