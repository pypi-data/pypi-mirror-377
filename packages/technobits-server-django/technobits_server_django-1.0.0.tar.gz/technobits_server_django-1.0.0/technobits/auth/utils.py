"""
Authentication Utilities for Technobits Library
"""

import logging
from typing import Optional, Tuple
from datetime import timedelta
from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class JWTCookieHelper:
    """
    Helper class for managing JWT tokens in HTTP-only cookies
    """
    
    # Cookie settings
    ACCESS_TOKEN_COOKIE = 'access_token'
    REFRESH_TOKEN_COOKIE = 'refresh_token'
    
    @classmethod
    def get_cookie_settings(cls) -> dict:
        """Get cookie configuration settings"""
        return {
            'max_age': getattr(settings, 'TECHNOBITS_COOKIE_MAX_AGE', 60 * 60 * 24 * 7),  # 7 days
            'httponly': True,
            'secure': getattr(settings, 'TECHNOBITS_COOKIE_SECURE', not settings.DEBUG),
            'samesite': getattr(settings, 'TECHNOBITS_COOKIE_SAMESITE', 'Lax'),
            'domain': getattr(settings, 'TECHNOBITS_COOKIE_DOMAIN', None),
        }
    
    @classmethod
    def set_jwt_cookies(cls, response: HttpResponse, user: User) -> HttpResponse:
        """
        Set JWT tokens as HTTP-only cookies
        """
        try:
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)
            
            # Get cookie settings
            cookie_settings = cls.get_cookie_settings()
            
            # Set access token cookie (shorter expiry)
            access_settings = cookie_settings.copy()
            access_settings['max_age'] = getattr(settings, 'TECHNOBITS_ACCESS_TOKEN_LIFETIME', 60 * 15)  # 15 minutes
            
            response.set_cookie(
                cls.ACCESS_TOKEN_COOKIE,
                access_token,
                **access_settings
            )
            
            # Set refresh token cookie (longer expiry)
            response.set_cookie(
                cls.REFRESH_TOKEN_COOKIE,
                refresh_token,
                **cookie_settings
            )
            
            logger.info(f"JWT cookies set for user: {user.email}")
            return response
            
        except Exception as e:
            logger.error(f"Error setting JWT cookies: {str(e)}")
            return response
    
    @classmethod
    def get_tokens_from_cookies(cls, request: HttpRequest) -> Tuple[Optional[str], Optional[str]]:
        """
        Extract JWT tokens from cookies
        """
        access_token = request.COOKIES.get(cls.ACCESS_TOKEN_COOKIE)
        refresh_token = request.COOKIES.get(cls.REFRESH_TOKEN_COOKIE)
        
        return access_token, refresh_token
    
    @classmethod
    def clear_jwt_cookies(cls, response: HttpResponse) -> HttpResponse:
        """
        Clear JWT cookies from response
        """
        cookie_settings = cls.get_cookie_settings()
        cookie_settings['max_age'] = 0
        
        response.set_cookie(cls.ACCESS_TOKEN_COOKIE, '', **cookie_settings)
        response.set_cookie(cls.REFRESH_TOKEN_COOKIE, '', **cookie_settings)
        
        # Also delete cookies
        response.delete_cookie(cls.ACCESS_TOKEN_COOKIE)
        response.delete_cookie(cls.REFRESH_TOKEN_COOKIE)
        
        logger.info("JWT cookies cleared")
        return response


class RequestHelper:
    """
    Helper for extracting request information
    """
    
    @staticmethod
    def get_client_ip(request: HttpRequest) -> str:
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    @staticmethod
    def get_user_agent(request: HttpRequest) -> str:
        """Get user agent from request"""
        return request.META.get('HTTP_USER_AGENT', '')
    
    @staticmethod
    def get_request_info(request: HttpRequest) -> dict:
        """Get comprehensive request information"""
        return {
            'ip_address': RequestHelper.get_client_ip(request),
            'user_agent': RequestHelper.get_user_agent(request),
            'method': request.method,
            'path': request.path,
            'timestamp': timezone.now().isoformat(),
        }


class PasswordHelper:
    """
    Helper for password-related operations
    """
    
    @staticmethod
    def generate_reset_token(user: User) -> str:
        """
        Generate a password reset token
        """
        from django.contrib.auth.tokens import default_token_generator
        from django.utils.http import urlsafe_base64_encode
        from django.utils.encoding import force_bytes
        
        # Generate token
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        return f"{uid}-{token}"
    
    @staticmethod
    def verify_reset_token(token: str) -> Tuple[bool, Optional[User]]:
        """
        Verify a password reset token and return user
        """
        try:
            from django.contrib.auth.tokens import default_token_generator
            from django.utils.http import urlsafe_base64_decode
            from django.utils.encoding import force_str
            
            # Parse token
            if '-' not in token:
                return False, None
                
            uid, token_part = token.rsplit('-', 1)
            
            # Decode user ID
            user_id = force_str(urlsafe_base64_decode(uid))
            user = User.objects.get(pk=user_id)
            
            # Verify token
            if default_token_generator.check_token(user, token_part):
                return True, user
            else:
                return False, None
                
        except (ValueError, User.DoesNotExist, OverflowError, TypeError):
            return False, None
    
    @staticmethod
    def is_password_strong(password: str) -> Tuple[bool, list]:
        """
        Check if password meets strength requirements
        """
        errors = []
        
        # Minimum length
        min_length = getattr(settings, 'TECHNOBITS_PASSWORD_MIN_LENGTH', 8)
        if len(password) < min_length:
            errors.append(f'Password must be at least {min_length} characters long')
        
        # Character requirements
        if getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_UPPERCASE', True):
            if not any(c.isupper() for c in password):
                errors.append('Password must contain at least one uppercase letter')
        
        if getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_LOWERCASE', True):
            if not any(c.islower() for c in password):
                errors.append('Password must contain at least one lowercase letter')
        
        if getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_DIGIT', True):
            if not any(c.isdigit() for c in password):
                errors.append('Password must contain at least one digit')
        
        if getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_SPECIAL', False):
            special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
            if not any(c in special_chars for c in password):
                errors.append('Password must contain at least one special character')
        
        return len(errors) == 0, errors


class TokenHelper:
    """
    Helper for token operations
    """
    
    @staticmethod
    def generate_api_key(length: int = 32) -> str:
        """Generate a random API key"""
        import secrets
        import string
        
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))
    
    @staticmethod
    def hash_token(token: str) -> str:
        """Hash a token for storage"""
        import hashlib
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def verify_token_hash(token: str, token_hash: str) -> bool:
        """Verify a token against its hash"""
        return TokenHelper.hash_token(token) == token_hash


class GoogleCredentialVerifier:
    """
    Enhanced Google OAuth credential verifier based on reference implementation
    """
    
    @classmethod
    def verify_credential(cls, credential: str) -> dict:
        """
        Verify Google credential and return user info.
        
        Args:
            credential: The credential string from Google Identity Services
            
        Returns:
            dict: User information from Google
            
        Raises:
            ValueError: If credential is invalid or verification fails
        """
        import os
        from django.conf import settings
        from google.oauth2 import id_token
        from google.auth.transport import requests as google_requests
        
        try:
            client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', None) or os.getenv('GOOGLE_OAUTH_CLIENT_ID')
            if not client_id:
                raise ValueError('Google Client ID not configured')
            
            # Verify the credential
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(), 
                client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False),
            }
            
        except ValueError as e:
            logger.error(f"Google credential verification failed: {str(e)}")
            raise ValueError(f"Invalid Google credential: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error during Google credential verification: {str(e)}")
            raise ValueError("Failed to verify Google credential")
    
    @classmethod
    def get_or_create_user_from_google(cls, google_info: dict):
        """
        Get or create a Django user from Google user information.
        
        Args:
            google_info: User information from Google
            
        Returns:
            User: Django user instance
        """
        from django.contrib.auth.models import User
        from .models import UserProfile
        
        email = google_info['email']
        google_id = google_info['google_id']
        
        try:
            # Try to get existing user by email
            user = User.objects.get(email=email)
            
            # Update user info if needed
            updated = False
            if not user.first_name and google_info.get('first_name'):
                user.first_name = google_info['first_name']
                updated = True
            if not user.last_name and google_info.get('last_name'):
                user.last_name = google_info['last_name']
                updated = True
            
            if updated:
                user.save()
            
            # Update or create profile
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'provider': 'google',
                    'google_id': google_id,
                    'avatar_url': google_info.get('picture', '')
                }
            )
            
            if not created and not profile.google_id:
                profile.google_id = google_id
                profile.provider = 'google'
                profile.avatar_url = google_info.get('picture', '')
                profile.save()
                
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create_user(
                username=email,
                email=email,
                first_name=google_info.get('first_name', ''),
                last_name=google_info.get('last_name', ''),
                # No password for Google users - they authenticate via Google
            )
            user.set_unusable_password()
            user.save()
            
            # Create profile
            UserProfile.objects.create(
                user=user,
                provider='google',
                google_id=google_id,
                avatar_url=google_info.get('picture', '')
            )
        
        return user


class RecaptchaVerifier:
    """
    reCAPTCHA verification utility
    """
    
    @classmethod
    def verify_recaptcha(cls, token: str, request: HttpRequest = None) -> Tuple[bool, str]:
        """
        Verify reCAPTCHA token with Google's API
        
        Args:
            token: reCAPTCHA response token
            request: HTTP request (for IP address)
            
        Returns:
            tuple: (success: bool, error_message: str)
        """
        import requests as http_requests
        import json
        from django.conf import settings
        
        # Check if reCAPTCHA is enabled
        secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', None)
        if not secret_key:
            logger.warning("reCAPTCHA secret key not configured - skipping verification")
            return True, ""  # Skip verification if not configured
        
        if not token:
            return False, "reCAPTCHA token is required"
        
        try:
            # Prepare verification request
            verify_url = "https://www.google.com/recaptcha/api/siteverify"
            data = {
                'secret': secret_key,
                'response': token,
            }
            
            # Add remote IP if available
            if request:
                remote_ip = RequestHelper.get_client_ip(request)
                if remote_ip:
                    data['remoteip'] = remote_ip
            
            # Make verification request
            response = http_requests.post(verify_url, data=data, timeout=10)
            result = response.json()
            
            if result.get('success', False):
                # Check score for v3 (optional)
                score = result.get('score', 1.0)
                min_score = getattr(settings, 'RECAPTCHA_MIN_SCORE', 0.5)
                
                if score >= min_score:
                    logger.info(f"reCAPTCHA verification successful (score: {score})")
                    return True, ""
                else:
                    logger.warning(f"reCAPTCHA score too low: {score} < {min_score}")
                    return False, "Security verification failed. Please try again."
            else:
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                return False, "Security verification failed. Please try again."
                
        except http_requests.exceptions.Timeout:
            logger.error("reCAPTCHA verification timeout")
            return False, "Security verification timeout. Please try again."
        except Exception as e:
            logger.error(f"reCAPTCHA verification error: {str(e)}")
            return False, "Security verification error. Please try again."
    
    @classmethod
    def is_recaptcha_enabled(cls) -> bool:
        """Check if reCAPTCHA is enabled"""
        from django.conf import settings
        return bool(getattr(settings, 'RECAPTCHA_SECRET_KEY', None))


class ValidationHelper:
    """
    Enhanced validation utilities
    """
    
    @staticmethod
    def validate_email_format(email: str) -> Tuple[bool, str]:
        """
        Validate email format
        """
        import re
        
        if not email:
            return False, "Email is required"
        
        # Basic email regex
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            return False, "Please enter a valid email address"
        
        # Check length
        if len(email) > 254:
            return False, "Email address is too long"
        
        return True, ""
    
    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """
        Validate name field
        """
        if not name:
            return False, "Name is required"
        
        name = name.strip()
        if len(name) < 1:
            return False, "Name cannot be empty"
        
        if len(name) > 100:
            return False, "Name is too long (maximum 100 characters)"
        
        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        import re
        if not re.match(r"^[a-zA-Z\s\-']+$", name):
            return False, "Name can only contain letters, spaces, hyphens, and apostrophes"
        
        return True, ""
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, list]:
        """
        Comprehensive password strength validation
        """
        return PasswordHelper.is_password_strong(password)
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize user input
        """
        if not input_str:
            return ""
        
        # Strip whitespace
        sanitized = input_str.strip()
        
        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')
        
        return sanitized


# Legacy aliases for backward compatibility
class _GoogleCredentialVerifier:
    """Legacy wrapper for GoogleAuthService"""
    
    @staticmethod
    def verify_credential(credential: str):
        return GoogleCredentialVerifier.verify_credential(credential)
    
    @staticmethod
    def get_or_create_user_from_google(google_info: dict):
        return GoogleCredentialVerifier.get_or_create_user_from_google(google_info)

