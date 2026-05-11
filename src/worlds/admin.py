from django.contrib import admin

from worlds.models import World, WorldCoverImage


class WorldCoverImageInline(admin.TabularInline):
    model = WorldCoverImage
    extra = 0
    fields = ("source", "status", "model_id", "is_active", "created_at")
    readonly_fields = ("created_at",)


@admin.register(World)
class WorldAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "genre", "updated_at")
    list_filter = ("genre", "created_at", "updated_at")
    search_fields = (
        "name",
        "description",
        "genre",
        "aesthetic_notes",
        "owner__username",
    )
    prepopulated_fields = {"slug": ("name",)}
    inlines = [WorldCoverImageInline]


@admin.register(WorldCoverImage)
class WorldCoverImageAdmin(admin.ModelAdmin):
    list_display = ("world", "source", "status", "model_id", "is_active", "updated_at")
    list_filter = ("source", "status", "is_active", "model_id")
    search_fields = ("world__name", "prompt", "error_message")
