from django.urls import path
from . import views

"""Account app URL patterns.

Visiting /auth/ previously returned 404 because there was no empty path ''
pattern. We add an index route now that lists all available auth endpoints
to make manual exploration in the browser easier.
"""

urlpatterns = [
    path("", views.api_index, name="auth_api_index"),  # /auth/
    path("signup/", views.signup, name="signup"),
    path("verify/", views.verify, name="verify"),
    path("login/", views.login, name="login"),
    path("password-reset-request/", views.password_reset_request, name="password_reset_request"),
    path("password-reset-confirm/", views.password_reset_confirm, name="password_reset_confirm"),
    path("me/", views.me, name="me"),
]