import json
import uuid


def test_password_reset_request_smoke(client):
    """
    Smoke test:
    - Signup a user
    - Call password-reset-request
    - Just check the server does NOT 500.
    """
    email = f"reset_{uuid.uuid4().hex[:8]}@mail.aub.edu"
    password = "ResetPass123!"

    # 1) Signup user
    signup_resp = client.post(
        "/auth/signup/",
        data=json.dumps({
            "name": "Reset User",
            "email": email,
            "password": password,
        }),
        content_type="application/json",
    )
    assert signup_resp.status_code in (200, 201)

    # 2) Request password reset
    resp = client.post(
        "/auth/password-reset-request/",
        data=json.dumps({"email": email}),
        content_type="application/json",
    )

    # For now, we only assert that the server doesn't blow up
    assert resp.status_code != 500
