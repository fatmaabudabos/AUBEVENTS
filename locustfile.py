"""Locust load test scenarios for the AUB Events backend.

Usage example:
    LOCUST_EMAIL=faa86@aub.edu.lb LOCUST_PASSWORD=Fafe&6666 \
    locust -f load_tests/locustfile.py --host http://localhost:8000

Environment variables:
    LOCUST_EMAIL        Email used for login (defaults to admin seed).
    LOCUST_PASSWORD     Password for the login user.
    LOCUST_EVENT_ID     Optional numeric event id for register/unregister tests.
"""
from __future__ import annotations

import logging
import os
import random
from typing import Dict, Optional

from locust import HttpUser, between, events, task

DEFAULT_EMAIL = "maa@aub.edu.lb"
DEFAULT_PASSWORD = "CSgrad@27"

LOGGER = logging.getLogger("locustfile")


def _parse_event_id(raw: Optional[str]) -> Optional[int]:
    if raw is None or not raw.strip():
        return None
    try:
        return int(raw)
    except ValueError:
        return None


EVENT_ID = _parse_event_id(os.getenv("LOCUST_EVENT_ID"))


@events.init.add_listener  # type: ignore[misc]
def on_test_start(environment, **_kwargs):
    if os.getenv("LOCUST_EVENT_ID") and EVENT_ID is None:
        LOGGER.warning("LOCUST_EVENT_ID is not a valid integer; register/unregister tasks disabled.")
    LOGGER.info("Locust configured with login email %s", os.getenv("LOCUST_EMAIL", DEFAULT_EMAIL))


class EventUser(HttpUser):
    """Simulate an authenticated attendee exercising high-traffic endpoints."""

    wait_time = between(1.0, 2.5)

    def on_start(self) -> None:
        self.token: Optional[str] = None
        self._login()

    def _login(self) -> None:
        email = os.getenv("LOCUST_EMAIL", DEFAULT_EMAIL)
        password = os.getenv("LOCUST_PASSWORD", DEFAULT_PASSWORD)
        with self.client.post(
            "/auth/login/",
            json={"email": email, "password": password},
            name="POST /auth/login",
            catch_response=True,
        ) as response:
            if response.status_code == 200:
                token = response.json().get("token") if response.content else None
                if token:
                    self.token = token
                    response.success()
                else:
                    response.failure("Login succeeded but no token returned")
            else:
                response.failure(f"Login failed with status {response.status_code}")

    def _auth_headers(self) -> Dict[str, str]:
        if not self.token:
            return {}
        return {"Authorization": f"Bearer {self.token}"}

    def _ensure_token(self) -> bool:
        if self.token:
            return True
        self._login()
        return self.token is not None

    @task(3)
    def list_events(self) -> None:
        self.client.get("/api/events", name="GET /api/events")

    @task(1)
    def list_my_events(self) -> None:
        if not self._ensure_token():
            return
        with self.client.get(
            "/api/my/events",
            headers=self._auth_headers(),
            name="GET /api/my/events",
            catch_response=True,
        ) as response:
            if response.status_code == 401:
                response.failure("Unauthorized; refreshing token")
                self.token = None
                self._login()
            elif response.status_code >= 500:
                response.failure(f"Server error {response.status_code}")
            else:
                response.success()

    @task(1)
    def toggle_registration(self) -> None:
        if EVENT_ID is None or not self._ensure_token():
            return
        if random.random() < 0.5:
            self._register_event(EVENT_ID)
        else:
            self._unregister_event(EVENT_ID)

    def _register_event(self, event_id: int) -> None:
        with self.client.post(
            "/api/events/register",
            json={"event_id": event_id},
            headers=self._auth_headers(),
            name="POST /api/events/register",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 409):
                response.success()
            elif response.status_code == 401:
                response.failure("Register unauthorized; refreshing token")
                self.token = None
                self._login()
            else:
                response.failure(f"Unexpected status {response.status_code}")

    def _unregister_event(self, event_id: int) -> None:
        with self.client.post(
            "/api/events/unregister",
            json={"event_id": event_id},
            headers=self._auth_headers(),
            name="POST /api/events/unregister",
            catch_response=True,
        ) as response:
            if response.status_code in (200, 400, 404):
                # Treat missing registrations as a successful round trip.
                response.success()
            elif response.status_code == 401:
                response.failure("Unregister unauthorized; refreshing token")
                self.token = None
                self._login()
            else:
                response.failure(f"Unexpected status {response.status_code}")
