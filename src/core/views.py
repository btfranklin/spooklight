from __future__ import annotations

from django.contrib.auth import get_user_model, login
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

DEMO_USERNAME = "demo"
DEMO_EMAIL = "demo@spooklight.local"


def landing(request: HttpRequest) -> HttpResponse:
    return render(request, "core/landing.html")


@require_POST
def demo_login(request: HttpRequest) -> HttpResponse:
    user_model = get_user_model()
    lookup = {user_model.USERNAME_FIELD: DEMO_USERNAME}
    user, created = user_model.objects.get_or_create(
        **lookup,
        defaults={"email": DEMO_EMAIL},
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])

    login(request, user, backend="django.contrib.auth.backends.ModelBackend")

    redirect_to = request.POST.get("next") or reverse("core:dashboard")
    if not url_has_allowed_host_and_scheme(
        redirect_to,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        redirect_to = reverse("core:dashboard")

    return redirect(redirect_to)


@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    return render(request, "core/dashboard.html")
