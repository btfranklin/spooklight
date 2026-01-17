from django.conf import settings


def test_django_settings_load() -> None:
    assert settings.DEBUG in {True, False}
