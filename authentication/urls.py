from django.urls import path

from . import views


urlpatterns = [
    path("register", views.UserRegister.as_view()),
    path("login", views.UserLogin.as_view()),
    path("profile", views.UserProfile.as_view()),
]
