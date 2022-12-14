from django.urls import path
import knox.views as knox

from . import views


urlpatterns = [
    path("register", views.UserRegister.as_view()),
    path("login", views.UserLogin.as_view()),
    path("profile", views.UserProfile.as_view()),
    path("logout", knox.LogoutView.as_view()),
    path("logoutall", knox.LogoutAllView.as_view()),
    path("change-pass", views.UserChangePassword.as_view()),
    path("forgot-pass", views.ForgotPassword.as_view()),
    path("send-otp", views.SendOTP.as_view()),
    path("validate-otp", views.ConfirmOTP.as_view()),
    path("tokens", views.UserTokens.as_view()),
]
