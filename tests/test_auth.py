import json
import uuid
import re

from django.core import mail


def test_signup_basic(client):
    """
    Simple smoke test:
    - Call /auth/signup/
    - Make sure the server doesn't crash
    - Expect 200 or 201 status
    """
    email = f"test_user_{uuid.uuid4().hex[:8]}@mail.aub.edu"

    payload = {
        "first_name": "Test",
        "last_name": "User",
        "email": email,
        "password": "StrongPass123!",
    }

    resp = client.post(
        "/auth/signup/",
        data=json.dumps(payload),
        content_type="application/json",
    )

    assert resp.status_code in (200, 201)


def test_login_after_signup(client):
    """
    Sign up a user, then try to login WITHOUT verifying → should be 403.
    """
    email = f"login_test_{uuid.uuid4().hex[:8]}@mail.aub.edu"
    password = "StrongPass456!"

    # 1) Signup
    signup_resp = client.post(
        "/auth/signup/",
        data=json.dumps({
            "first_name": "Login",
            "last_name": "Test",
            "email": email,
            "password": password
        }),
        content_type="application/json",
    )
    assert signup_resp.status_code in (200, 201)

    # 2) Try login without verification
    login_resp = client.post(
        "/auth/login/",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )

    assert login_resp.status_code == 403


def test_signup_verify_and_login(client):
    """
    Signup -> get code from email -> verify -> login -> expect token.
    If no email is sent in this environment, skip the test.
    """
    email = f"verify_test_{uuid.uuid4().hex[:8]}@mail.aub.edu"
    password = "StrongPass789!"

    # 1) Signup
    signup_resp = client.post(
        "/auth/signup/",
        data=json.dumps({
            "first_name": "Verify",
            "last_name": "Test",
            "email": email,
            "password": password
        }),
        content_type="application/json",
    )
    assert signup_resp.status_code in (200, 201)

    # 2) If no email has been sent, skip this test for now
    if len(mail.outbox) == 0:
        import pytest
        pytest.skip("Signup did not send an email in test environment; skipping verify+login flow.")

    last_email = mail.outbox[-1]
    body = last_email.body

    matches = re.findall(r"\b\d{6}\b", body)
    assert matches, "No 6-digit code found in email body"
    code = matches[0]

    # 3) Verify
    verify_resp = client.post(
        "/auth/verify/",
        data=json.dumps({"email": email, "token": code}),
        content_type="application/json",
    )
    assert verify_resp.status_code in (200, 204)

    # 4) Login (now should be allowed)
    login_resp = client.post(
        "/auth/login/",
        data=json.dumps({"email": email, "password": password}),
        content_type="application/json",
    )
    assert login_resp.status_code == 200
    data = login_resp.json()
    assert "token" in data
def test_login_wrong_password(client):
    """
    Signup with a password, then try to login with a WRONG password.
    Should return 401 or 403 (not allowed).
    """
    email = f"wrongpass_{uuid.uuid4().hex[:8]}@mail.aub.edu"
    correct_password = "CorrectPass123!"
    wrong_password = "WrongPass999!"

    # 1) Signup
    signup_resp = client.post(
        "/auth/signup/",
        data=json.dumps({
            "first_name": "Wrong",
            "last_name": "Pass",
            "email": email,
            "password": correct_password,
        }),
        content_type="application/json",
    )
    assert signup_resp.status_code in (200, 201)

    # 2) Try login with wrong password
    login_resp = client.post(
        "/auth/login/",
        data=json.dumps({
            "email": email,
            "password": wrong_password,
        }),
        content_type="application/json",
    )

    # Backend should *not* let this pass
    assert login_resp.status_code in (401, 403)