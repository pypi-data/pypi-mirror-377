"""
Authentication Services for Technobits Library
"""

import logging
import requests
from typing import Optional, Dict, Tuple
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.utils import timezone
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .models import UserProfile, LoginAttempt
from .utils import RecaptchaVerifier, ValidationHelper

logger = logging.getLogger(__name__)


class RecaptchaService:
    """
    reCAPTCHA verification service
    """
    
    @staticmethod
    def verify_token(token: str, action: str = None, ip_address: str = None) -> Tuple[bool, Dict]:
        """
        Verify reCAPTCHA token
        
        Args:
            token: reCAPTCHA response token
            action: Action name (for v3)
            ip_address: Client IP address
            
        Returns:
            tuple: (success: bool, result: dict)
        """
        try:
            from django.http import HttpRequest
            
            # Create a mock request object for IP
            class MockRequest:
                def __init__(self, ip):
                    self.META = {'REMOTE_ADDR': ip} if ip else {}
            
            mock_request = MockRequest(ip_address) if ip_address else None
            success, error_message = RecaptchaVerifier.verify_recaptcha(token, mock_request)
            
            result = {
                'success': success,
                'error_message': error_message,
                'action': action,
                'ip_address': ip_address
            }
            
            return success, result
            
        except Exception as e:
            logger.error(f"reCAPTCHA service error: {str(e)}")
            return False, {'success': False, 'error_message': 'reCAPTCHA verification failed'}
    
    @staticmethod
    def is_enabled() -> bool:
        """Check if reCAPTCHA is enabled"""
        return RecaptchaVerifier.is_recaptcha_enabled()


class AuthService:
    """
    Core authentication service
    """
    
    @staticmethod
    def create_user_with_profile(email: str, password: str = None, **kwargs) -> User:
        """
        Create a new user with associated profile
        """
        # Extract profile fields
        first_name = kwargs.pop('first_name', '')
        last_name = kwargs.pop('last_name', '')
        provider = kwargs.pop('provider', 'email')
        google_id = kwargs.pop('google_id', None)
        avatar_url = kwargs.pop('avatar_url', '')
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password
        )
        
        # Create profile
        profile = UserProfile.objects.create(
            user=user,
            provider=provider,
            google_id=google_id,
            avatar_url=avatar_url,
            **kwargs
        )
        
        logger.info(f"Created user {email} with provider {provider}")
        return user
    
    @staticmethod
    def authenticate_user(email: str, password: str, ip_address: str = None, user_agent: str = None) -> Tuple[bool, Optional[User], str]:
        """
        Authenticate user and log attempt
        """
        try:
            user = authenticate(username=email, password=password)
            
            if user and user.is_active:
                # Log successful attempt
                LoginAttempt.objects.create(
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=True
                )
                
                # Update profile last login IP
                if hasattr(user, 'technobits_profile'):
                    user.technobits_profile.last_login_ip = ip_address
                    user.technobits_profile.save()
                
                return True, user, "Authentication successful"
            else:
                reason = "User inactive" if user else "Invalid credentials"
                
                # Log failed attempt
                LoginAttempt.objects.create(
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    success=False,
                    failure_reason=reason
                )
                
                return False, None, reason
                
        except Exception as e:
            logger.error(f"Authentication error for {email}: {str(e)}")
            
            # Log failed attempt
            LoginAttempt.objects.create(
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=False,
                failure_reason="System error"
            )
            
            return False, None, "Authentication failed"
    
    @staticmethod
    def get_login_attempts(email: str = None, ip_address: str = None, hours: int = 24) -> int:
        """
        Get recent login attempts count
        """
        from datetime import timedelta
        
        since = timezone.now() - timedelta(hours=hours)
        queryset = LoginAttempt.objects.filter(timestamp__gte=since)
        
        if email:
            queryset = queryset.filter(email=email)
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
            
        return queryset.count()
    
    @staticmethod
    def is_rate_limited(email: str = None, ip_address: str = None) -> bool:
        """
        Check if user/IP is rate limited
        """
        max_attempts = getattr(settings, 'TECHNOBITS_MAX_LOGIN_ATTEMPTS', 5)
        
        if email:
            attempts = AuthService.get_login_attempts(email=email, hours=1)
            if attempts >= max_attempts:
                return True
                
        if ip_address:
            attempts = AuthService.get_login_attempts(ip_address=ip_address, hours=1)
            if attempts >= max_attempts * 3:  # More lenient for IP
                return True
                
        return False


class GoogleAuthService:
    """
    Google OAuth authentication service
    """
    
    def __init__(self):
        self.client_id = getattr(settings, 'GOOGLE_OAUTH_CLIENT_ID', '')
        if not self.client_id:
            logger.warning("GOOGLE_OAUTH_CLIENT_ID not configured")
    
    def verify_credential(self, credential: str) -> Dict:
        """
        Verify Google OAuth credential and return user info
        """
        try:
            # Verify the credential with Google
            idinfo = id_token.verify_oauth2_token(
                credential, 
                google_requests.Request(), 
                self.client_id
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'first_name': idinfo.get('given_name', ''),
                'last_name': idinfo.get('family_name', ''),
                'avatar_url': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False),
            }
            
        except ValueError as e:
            logger.error(f"Google credential verification failed: {str(e)}")
            raise ValueError(f"Invalid Google credential: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error verifying Google credential: {str(e)}")
            raise ValueError("Google authentication failed")
    
    def get_or_create_user_from_google(self, google_info: Dict) -> User:
        """
        Get or create user from Google info
        """
        email = google_info['email']
        google_id = google_info['google_id']
        
        # Check if user exists by Google ID
        try:
            profile = UserProfile.objects.get(google_id=google_id)
            user = profile.user
            
            # Update user info if needed
            if user.email != email:
                user.email = email
                user.username = email
                user.save()
                
            logger.info(f"Found existing Google user: {email}")
            return user
            
        except UserProfile.DoesNotExist:
            pass
        
        # Check if user exists by email
        try:
            user = User.objects.get(email=email)
            
            # Link Google account to existing user
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'provider': 'google',
                    'google_id': google_id,
                    'avatar_url': google_info.get('avatar_url', '')
                }
            )
            
            if not created:
                # Update existing profile
                profile.google_id = google_id
                profile.provider = 'google'
                profile.avatar_url = google_info.get('avatar_url', '')
                profile.save()
            
            logger.info(f"Linked Google account to existing user: {email}")
            return user
            
        except User.DoesNotExist:
            pass
        
        # Create new user
        user = AuthService.create_user_with_profile(
            email=email,
            first_name=google_info.get('first_name', ''),
            last_name=google_info.get('last_name', ''),
            provider='google',
            google_id=google_id,
            avatar_url=google_info.get('avatar_url', '')
        )
        
        logger.info(f"Created new Google user: {email}")
        return user


class RecaptchaService:
    """
    reCAPTCHA verification service
    """
    
    def __init__(self):
        self.secret_key = getattr(settings, 'RECAPTCHA_SECRET_KEY', '')
        self.verify_url = 'https://www.google.com/recaptcha/api/siteverify'
        self.enabled = bool(self.secret_key)
        
        if not self.enabled:
            logger.warning("RECAPTCHA_SECRET_KEY not configured - reCAPTCHA verification disabled")
    
    def verify_token(self, token: str, action: str = None, ip_address: str = None) -> Tuple[bool, Dict]:
        """
        Verify reCAPTCHA token
        """
        if not self.enabled:
            logger.info("reCAPTCHA verification skipped (not configured)")
            return True, {'skip_reason': 'not_configured'}
        
        if not token:
            logger.warning("No reCAPTCHA token provided")
            return False, {'error': 'no_token'}
        
        try:
            data = {
                'secret': self.secret_key,
                'response': token,
            }
            
            if ip_address:
                data['remoteip'] = ip_address
            
            response = requests.post(self.verify_url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            
            if result.get('success'):
                score = result.get('score', 1.0)
                min_score = getattr(settings, 'RECAPTCHA_MIN_SCORE', 0.5)
                
                if score >= min_score:
                    logger.info(f"reCAPTCHA verification successful - score: {score}")
                    return True, result
                else:
                    logger.warning(f"reCAPTCHA score too low: {score} < {min_score}")
                    return False, {'error': 'low_score', 'score': score}
            else:
                error_codes = result.get('error-codes', [])
                logger.warning(f"reCAPTCHA verification failed: {error_codes}")
                return False, {'error': 'verification_failed', 'error_codes': error_codes}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"reCAPTCHA API request failed: {str(e)}")
            return False, {'error': 'api_error', 'message': str(e)}
        except Exception as e:
            logger.error(f"Unexpected reCAPTCHA verification error: {str(e)}")
            return False, {'error': 'unknown_error', 'message': str(e)}

