from __future__ import annotations

from django.contrib import admin

from ai_tasks.models import AITask, AITaskEvent, AIWorkerHeartbeat


class AITaskEventInline(admin.TabularInline):
    model = AITaskEvent
    extra = 0
    readonly_fields = ["sequence", "event_type", "payload", "created_at"]
    can_delete = False


@admin.register(AITask)
class AITaskAdmin(admin.ModelAdmin):
    list_display = ["id", "kind", "status", "owner", "world", "updated_at"]
    list_filter = ["kind", "status", "provider"]
    search_fields = ["id", "queue_job_id", "provider_request_id", "error_message"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [AITaskEventInline]


@admin.register(AIWorkerHeartbeat)
class AIWorkerHeartbeatAdmin(admin.ModelAdmin):
    list_display = ["worker_id", "last_seen_at", "updated_at"]
    readonly_fields = ["created_at", "updated_at"]
