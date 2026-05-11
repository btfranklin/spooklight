from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
import pytest


def test_django_settings_load() -> None:
    assert settings.DEBUG in {True, False}


def test_landing_page_renders_for_anonymous_user(client: Client) -> None:
    response = client.get(reverse("core:landing"))

    assert response.status_code == 200
    assert b"Bring your imagined worlds to life." in response.content


@pytest.mark.django_db
def test_landing_page_redirects_authenticated_user_to_dashboard(
    client: Client,
) -> None:
    user_model = get_user_model()
    user = user_model.objects.create_user(username="authenticated")
    client.force_login(user)

    response = client.get(reverse("core:landing"))

    assert response.status_code == 302
    assert response["Location"] == reverse("core:dashboard")
