from django.urls import path

from core import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("demo-login/", views.demo_login, name="demo_login"),
    path("dashboard/", views.dashboard, name="dashboard"),
]
