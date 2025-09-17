"""
Authentication URLs for Technobits Library
"""

from django.urls import path
from . import views

app_name = 'technobits_auth'

urlpatterns = [
    # Authentication endpoints
    path('register/', views.RegisterView, name='register'),
    path('login/', views.LoginView, name='login'),
    path('google/', views.GoogleLoginView, name='google_login'),
    path('logout/', views.LogoutView, name='logout'),
    path('refresh/', views.RefreshTokenView, name='refresh_token'),
    path('me/', views.MeView, name='me'),
    
    # Password management
    path('forgot-password/', views.ForgotPasswordView, name='forgot_password'),
    path('reset-password/', views.ResetPasswordView, name='reset_password'),
    path('change-password/', views.ChangePasswordView, name='change_password'),
    
    # Health check
    path('health/', views.HealthView, name='health'),
]

