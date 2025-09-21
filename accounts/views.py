import re
import bcrypt
import secrets
import random
import jwt
import bcrypt
from django.conf import settings
from datetime import datetime, timedelta
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.mail import send_mail
from database.database import (
    create_user, get_user, update_verification_token,
    get_verification_token, get_verification_token_expiry,
     update_is_verified,  get_password, get_is_verified,
)

USERS_DB = {}   # temporary in-memory store for testing


def is_aub_email(email: str) -> bool:
    """Check if the email ends with @aub.edu.lb"""
    return email.lower().endswith("@aub.edu.lb")


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


@api_view(["POST"])
def signup(request):
    email = request.data.get("email")
    password = request.data.get("password")

    # 1. Validate input
    if not email or not password:
        return Response({"error": "Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)

    # 2. Check AUB domain
    if not email.lower().endswith("@aub.edu.lb"):
        return Response({"error": "Only AUB emails are allowed."}, status=status.HTTP_400_BAD_REQUEST)

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
    send_mail(
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