from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from database.database import create_user, get_user, update_is_verified, update_reset_code, delete_user
import bcrypt
from datetime import datetime, timedelta
from sqlmodel import SQLModel
from database.database import get_engine

class PasswordResetTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        SQLModel.metadata.create_all(get_engine())

    def setUp(self):
        self.client = APIClient()
        self.email = "test@aub.edu.lb"
        self.password = "TestPass123!"
        from django.core.cache import cache
        delete_user(self.email)  # Remove any existing user before each test
        # Clear rate limit cache for this email
        cache.delete(f"reset-rl-{self.email}")
        pw_hash = bcrypt.hashpw(self.password.encode(), bcrypt.gensalt()).decode()
        create_user(self.email, pw_hash, "Test", "User")
        update_is_verified(self.email, True)

    def test_password_reset_request_success(self):
        response = self.client.post("/auth/password-reset-request/", {"email": self.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_password_reset_request_nonexistent_email(self):
        response = self.client.post("/auth/password-reset-request/", {"email": "nouser@aub.edu.lb"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_password_reset_request_rate_limit(self):
        for _ in range(3):
            self.client.post("/auth/password-reset-request/", {"email": self.email}, format='json')
        response = self.client.post("/auth/password-reset-request/", {"email": self.email}, format='json')
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_password_reset_confirm_success(self):
        # Simulate a reset code
        reset_code = "123456"
        expiry = datetime.utcnow() + timedelta(minutes=15)
        update_reset_code(self.email, reset_code, expiry)
        new_password = "NewPass123!"
        response = self.client.post("/auth/password-reset-confirm/", {
            "email": self.email,
            "reset_code": reset_code,
            "new_password": new_password
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("message", response.data)

    def test_password_reset_confirm_invalid_code(self):
        reset_code = "654321"
        expiry = datetime.utcnow() + timedelta(minutes=15)
        update_reset_code(self.email, reset_code, expiry)
        response = self.client.post("/auth/password-reset-confirm/", {
            "email": self.email,
            "reset_code": "wrongcode",
            "new_password": "NewPass123!"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_expired_code(self):
        reset_code = "123456"
        expiry = datetime.utcnow() - timedelta(minutes=1)
        update_reset_code(self.email, reset_code, expiry)
        response = self.client.post("/auth/password-reset-confirm/", {
            "email": self.email,
            "reset_code": reset_code,
            "new_password": "NewPass123!"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_reset_confirm_weak_password(self):
        reset_code = "123456"
        expiry = datetime.utcnow() + timedelta(minutes=15)
        update_reset_code(self.email, reset_code, expiry)
        response = self.client.post("/auth/password-reset-confirm/", {
            "email": self.email,
            "reset_code": reset_code,
            "new_password": "weak"
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
