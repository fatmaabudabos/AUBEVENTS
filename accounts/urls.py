from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("verify/", views.verify, name="verify"),
    path("login/", views.login, name="login"),
    path("password-reset-request/", views.password_reset_request, name="password_reset_request"),
    path("password-reset-confirm/", views.password_reset_confirm, name="password_reset_confirm"),
]