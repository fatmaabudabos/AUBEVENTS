import json
import uuid


def _signup_and_login(client):
    """
    Helper:
    - Sign up a fresh user
    - Try login (may be blocked if verify is required)
    - Return (status_code, data/json or None)
    """
    email = f"events_user_{uuid.uuid4().hex[:8]}@mail.aub.edu"
    password = "EventsPass123!"

    # Signup
    signup_resp = client.post(
        "/auth/signup/",
        data=json.dumps({
            "first_name": "Events",
            "last_name": "User",
            "email": email,
            "password": password
        }),
        content_type="application/json",
    )
    assert signup_resp.status_code in (200, 201)

    # Login (may be 403 if your backend strictly requires verification)
    login_resp = client.post(
        "/auth/login/",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )

    try:
        data = login_resp.json()
    except Exception:
        data = None

    return login_resp.status_code, data


def test_events_no_auth(client):
    """
    Call events endpoint without auth.
    Just make sure server doesn't crash (no 500).
    """
    # Try both common paths – one of them should exist in your URLs.
    possible_paths = ["/api/events", "/api/events/", "/events/", "/events"]

    got_non_404 = False

    for path in possible_paths:
        resp = client.get(path)
        # If it's 404 → maybe not that path, try next
        if resp.status_code != 404:
            got_non_404 = True
            # Whatever it is (200, 401, 403...), it should NOT be 500
            assert resp.status_code != 500
            break

    assert got_non_404, "All tested event paths returned 404 – check URLs config"


def test_events_with_auth_smoke(client):
    """
    Try calling events with an auth token (if login succeeds).
    Again: just ensure no 500, not the exact behavior.
    """
    status, data = _signup_and_login(client)

    # If login is blocked by verification (403), we can't test auth header yet.
    if status != 200 or not data or "token" not in data:
        # For now just skip this test in that case
        import pytest
        pytest.skip("Login did not return a token (likely requires email verification).")

    token = data["token"]

    possible_paths = ["/api/events", "/api/events/", "/events/", "/events"]

    got_non_404 = False

    for path in possible_paths:
        resp = client.get(path, HTTP_AUTHORIZATION=f"Bearer {token}")
        if resp.status_code != 404:
            got_non_404 = True
            assert resp.status_code != 500
            break

    assert got_non_404, "All tested event paths returned 404 with auth – check URLs config"
