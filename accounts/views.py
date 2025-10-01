# All imports at the top
import re
import bcrypt
import secrets
import random
import jwt
import logging
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import json
import requests
from database.database import (
    create_user, get_user, update_verification_token,
    get_verification_token, get_verification_token_expiry,
    update_is_verified,  get_password, get_is_verified,
    update_reset_code, get_reset_code, get_reset_code_expiry
)

logger = logging.getLogger(__name__)


def safe_send_mail(*args, **kwargs):
    """Send an email using SendGrid REST API if API key available, else fallback to Django send_mail.

    Returns 1 if queued/sent, 0 otherwise. Never raises to caller.
    """
    subject = kwargs.get('subject') or (len(args) > 0 and args[0])
    message = kwargs.get('message') or (len(args) > 1 and args[1])
    # Always force using VERIFIED_FROM_EMAIL to avoid accidental unverified 'from' causing 403/550.
    from_email = settings.VERIFIED_FROM_EMAIL
    recipient_list = kwargs.get('recipient_list') or (len(args) > 3 and args[3]) or []

    if settings.SENDGRID_API_KEY:
        logger.debug("Attempting SendGrid REST send from %s to %s", from_email, recipient_list)
        try:
            resp = requests.post(
                'https://api.sendgrid.com/v3/mail/send',
                headers={
                    'Authorization': f'Bearer {settings.SENDGRID_API_KEY}',
                    'Content-Type': 'application/json'
                },
                data=json.dumps({
                    'personalizations': [{ 'to': [{'email': r} for r in recipient_list] }],
                    'from': { 'email': from_email },
                    'subject': subject,
                    'content': [{ 'type': 'text/plain', 'value': message }]
                }),
                timeout=10
            )
            if 200 <= resp.status_code < 300:
                logger.debug("SendGrid accepted message for %s", recipient_list)
                return 1
            else:
                logger.warning("SendGrid API failure %s: %s", resp.status_code, resp.text[:300])
        except Exception as exc:
            logger.warning("SendGrid API exception: %s", exc)
        # fallback to Django backend if API attempt failed
    try:
        logger.debug("Falling back to Django send_mail backend from %s", from_email)
        return send_mail(*args, **kwargs)
    except Exception as exc:
        logger.warning("Django send_mail failed: %s", exc)
        return 0


@csrf_exempt
@api_view(["GET"])
def api_index(request):
    """Return a simple listing of available auth endpoints.

    This helps when a user visits /auth/ in the browser and previously saw 404.
    """
    base = request.build_absolute_uri('/')[:-1]  # remove trailing slash
    auth_base = f"{base}/auth"
    return Response({
        "endpoints": {
            "signup": f"{auth_base}/signup/",
            "verify": f"{auth_base}/verify/",
            "login": f"{auth_base}/login/",
            "password_reset_request": f"{auth_base}/password-reset-request/",
            "password_reset_confirm": f"{auth_base}/password-reset-confirm/",
            "me": f"{auth_base}/me/",
        },
        "notes": "Use POST for all except 'me' (GET). All bodies JSON."}, status=status.HTTP_200_OK)


def _auth_from_request(request):
    """Return user (or None) from Authorization: Bearer <jwt> header."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1].strip()
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except Exception:
        return None
    email = payload.get("email")
    if not email:
        return None
    return get_user(email)


@csrf_exempt
@api_view(["GET"])
def me(request):
    user = _auth_from_request(request)
    if not user:
        return Response({"error": "Unauthorized"}, status=status.HTTP_401_UNAUTHORIZED)
    return Response({
        "email": user.email,
        "is_verified": user.is_verified,
        "is_admin": getattr(user, "is_admin", False),
    }, status=status.HTTP_200_OK)

@csrf_exempt
@api_view(["POST"])
def password_reset_request(request):
    # Extract email first
    email = request.data.get("email")
    if not email:
        return Response({"error": "Email is required."}, status=status.HTTP_400_BAD_REQUEST)
    # Rate limit: max 3 requests per hour per email
    key = f"reset-rl-{email}"
    count = cache.get(key, 0)
    if count >= 3:
        return Response({"error": "Too many password reset requests. Please try again later."}, status=status.HTTP_429_TOO_MANY_REQUESTS)
    cache.set(key, count + 1, timeout=3600)  # 1 hour
    user = get_user(email)
    if not user:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    # Generate a secure reset code (6-digit)
    reset_code = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(minutes=15)
    update_reset_code(email, reset_code, expiry)
    # Send email with reset code
    safe_send_mail(
        subject="AUBEvents Password Reset",
        message=f"Your password reset code is: {reset_code}\nThis code will expire in 15 minutes.",
        from_email=None,
        recipient_list=[email],
    )
    return Response({"message": "Password reset code sent to your email."}, status=status.HTTP_200_OK)

USERS_DB = {}   # temporary in-memory store for testing


ALLOWED_EMAIL_DOMAINS = {"aub.edu.lb", "mail.aub.edu"}


def is_aub_email(email: str) -> bool:
    """Return True if email domain is allowed (aub.edu.lb or mail.aub.edu)."""
    email = email.lower().strip()
    if "@" not in email:
        return False
    domain = email.rsplit("@", 1)[1]
    return domain in ALLOWED_EMAIL_DOMAINS


def check_password_strength(password: str) -> tuple[bool, str]:
    """Enforce simple password strength rules."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return False, "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return False, "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return False, "Password must contain at least one digit."
    if not re.search(r"[@$!%*?&]", password):
        return False, "Password must contain at least one special character (@$!%*?&)."
    return True, "OK"


@csrf_exempt
@api_view(["POST"])
def signup(request):
    email = request.data.get("email")
    password = request.data.get("password")

    # 1. Validate input
    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Check domain
    if not is_aub_email(email):
        return Response({"error": "Only AUB (aub.edu.lb / mail.aub.edu) emails are allowed."}, status=status.HTTP_400_BAD_REQUEST)

    # 3. Enforce password strength
    ok, msg = check_password_strength(password)
    if not ok:
        return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)

    # 4. Check duplicate
    if get_user(email):  # DB lookup
        return Response({"error": "Email already registered."}, status=status.HTTP_409_CONFLICT)

    # 5. Hash password
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    # 6. Create user (inactive by default)
    create_user(email, pw_hash)

    # 7. Generate verification token
    token = str(random.randint(100000, 999999))
    expiry = datetime.utcnow() + timedelta(hours=0.2)
    update_verification_token(email, token, expiry)

    # 8. Send verification email
    safe_send_mail(
        subject="Verify your AUBEvents account",
        message=f"Hello,\n\nYour verification code is: {token}\nThis code will expire in 10 minutes.\n\nBest,\nAUBEvents Team",
        from_email=None,  # defaults to DEFAULT_FROM_EMAIL in settings.py
        recipient_list=[email],
    )

    # 9. Respond (we'll change this to email verification)
    return Response(
        {"message": "Signup successful. Please verify your email.", "verification_token": token},
        status=status.HTTP_201_CREATED
    )

@csrf_exempt
@api_view(["POST"])
def verify(request):
    email = request.data.get("email")
    token = request.data.get("token")

    # 1. Validate input
    if not email or not token:
        return Response({"error": "Email and token are required."}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Find user
    user = get_user(email)
    if not user:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    # 3. Check if already verified
    if get_is_verified(email):  # assuming Khalil’s Users model has `is_verified`
       return Response({"message": "Account already verified."}, status=status.HTTP_200_OK)

    # 4. Get stored token + expiry
    stored_token = get_verification_token(email)
    expiry = get_verification_token_expiry(email)

    if not stored_token or not expiry:
        return Response({"error": "No verification token found."}, status=status.HTTP_400_BAD_REQUEST)

    # 5. Validate token
    if stored_token != token:
        return Response({"error": "Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
    # 6. Check expiry
    if datetime.utcnow() > expiry:
        return Response({"error": "Token has expired."}, status=status.HTTP_400_BAD_REQUEST)

    # 7.mark as verified
    update_is_verified(email, True)

    return Response({"message": "Account verified successfully."}, status=status.HTTP_200_OK)

    
@csrf_exempt
@api_view(["POST"])
def login(request):
    email = request.data.get("email")
    password = request.data.get("password")

    # 1. Input validation
    if not email or not password:
        return Response(
            {"error": "Email and password are required."},
            status=status.HTTP_400_BAD_REQUEST
        )

    # 2. Check user exists
    user = get_user(email)
    if not user:
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 3. Check if verified
    if not get_is_verified(email):
        return Response(
            {"error": "Please verify your account first."},
            status=status.HTTP_403_FORBIDDEN
        )

    # 4. Check password
    stored_pw = get_password(email)
    if not stored_pw or not bcrypt.checkpw(password.encode("utf-8"), stored_pw.encode("utf-8")):
        return Response(
            {"error": "Invalid email or password."},
            status=status.HTTP_401_UNAUTHORIZED
        )

    # 5. Generate JWT
    payload = {
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRY_HOURS),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return Response(
        {
            "message": "Login successful",
            "token": token
        },
        status=status.HTTP_200_OK
    )

@csrf_exempt
@api_view(["POST"])
def password_reset_confirm(request):
    email = request.data.get("email")
    reset_code = request.data.get("reset_code")
    new_password = request.data.get("new_password")
    if not email or not reset_code or not new_password:
        return Response({"error": "Email, reset code, and new password are required."}, status=status.HTTP_400_BAD_REQUEST)
    user = get_user(email)
    if not user:
        return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    stored_code = get_reset_code(email)
    expiry = get_reset_code_expiry(email)
    if not stored_code or not expiry:
        return Response({"error": "No reset code found. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)
    if stored_code != reset_code:
        return Response({"error": "Invalid reset code."}, status=status.HTTP_400_BAD_REQUEST)
    if datetime.utcnow() > expiry:
        return Response({"error": "Reset code has expired."}, status=status.HTTP_400_BAD_REQUEST)
    ok, msg = check_password_strength(new_password)
    if not ok:
        return Response({"error": msg}, status=status.HTTP_400_BAD_REQUEST)
    pw_hash = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt()).decode()
    from database.database import update_password, update_reset_code
    update_password(email, pw_hash)
    # Clear reset code and expiry
    update_reset_code(email, None, None)
    return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)