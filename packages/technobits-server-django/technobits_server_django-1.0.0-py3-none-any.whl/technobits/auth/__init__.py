"""
Technobits Authentication Module
Provides complete authentication system with Google OAuth, JWT, and reCAPTCHA
"""

# Lazy imports to avoid circular dependencies during Django startup
# These can be imported at runtime when needed
# from .views import (
#     RegisterView,
#     LoginView,
#     GoogleLoginView,
#     RefreshTokenView,
#     MeView,
#     LogoutView,
#     ForgotPasswordView,
#     ResetPasswordView,
#     ChangePasswordView,
#     HealthView,
# )

# from .serializers import (
#     RegisterSerializer,
#     LoginSerializer,
#     GoogleLoginSerializer,
#     UserSerializer,
#     ForgotPasswordSerializer,
#     ResetPasswordSerializer,
# )

# from .utils import (
#     JWTCookieHelper,
#     GoogleCredentialVerifier,
# )

# from .services import (
#     AuthService,
#     GoogleAuthService,
#     RecaptchaService,
# )

from .apps import TechnobitsAuthConfig

__all__ = [
    # Views
    "RegisterView",
    "LoginView", 
    "GoogleLoginView",
    "RefreshTokenView",
    "MeView",
    "LogoutView",
    "ForgotPasswordView",
    "ResetPasswordView",
    "ChangePasswordView",
    "HealthView",
    
    # Serializers
    "RegisterSerializer",
    "LoginSerializer",
    "GoogleLoginSerializer", 
    "UserSerializer",
    "ForgotPasswordSerializer",
    "ResetPasswordSerializer",
    
    # Utils
    "JWTCookieHelper",
    "GoogleCredentialVerifier",
    
    # Services
    "AuthService",
    "GoogleAuthService",
    "RecaptchaService",
    
    # Apps
    "TechnobitsAuthConfig",
]

