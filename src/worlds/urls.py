from django.urls import include, path

from worlds import views

app_name = "worlds"

urlpatterns = [
    path("new/", views.create_world, name="create"),
    path(
        "<slug:slug>/artifacts/",
        include("world_artifacts.urls", namespace="world_artifacts"),
    ),
    path("<slug:slug>/", views.world_detail, name="detail"),
    path("<slug:slug>/generate-cover/", views.generate_cover, name="generate_cover"),
    path(
        "<slug:slug>/cover-status/",
        views.cover_status_fragment,
        name="cover_status",
    ),
]
