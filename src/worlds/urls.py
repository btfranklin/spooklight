from django.urls import path

from worlds import views

app_name = "worlds"

urlpatterns = [
    path("new/", views.create_world, name="create"),
    path("<slug:slug>/", views.world_detail, name="detail"),
    path("<slug:slug>/generate-cover/", views.generate_cover, name="generate_cover"),
]
