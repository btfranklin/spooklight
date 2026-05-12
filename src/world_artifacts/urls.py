from django.urls import path

from world_artifacts import views

app_name = "world_artifacts"

urlpatterns = [
    path("aesthetics/edit/", views.edit_aesthetics, name="edit_aesthetics"),
    path("truths/new/", views.create_truth, name="create_truth"),
    path("characters/new/", views.create_character, name="create_character"),
    path("locations/new/", views.create_location, name="create_location"),
    path("events/new/", views.create_event, name="create_event"),
    path("images/new/", views.create_image, name="create_image"),
    path("stories/new/", views.create_story, name="create_story"),
]
