from django.urls import path
from . import views

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("verify/", views.verify, name="verify"),
    path("login/", views.login, name="login"),
]