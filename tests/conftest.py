# tests/conftest.py
import os
import pytest

# Tell pytest which Django settings to use
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

@pytest.fixture
def client(db):
    """
    Django test client fixture.
    Usage in tests:
        def test_something(client):
            resp = client.get("/auth/me/")
    """
    from django.test import Client
    return Client()
import os
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings")

@pytest.fixture(autouse=True)
def _test_settings(settings):
    # Use in-memory email backend for tests
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

@pytest.fixture
def client(db):
    from django.test import Client
    return Client()
