"""
Authentication Serializers for Technobits Library
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError

from .services import AuthService, GoogleAuthService, RecaptchaService
from .utils import PasswordHelper, RequestHelper


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    display_name = serializers.SerializerMethodField()
    avatar_url = serializers.SerializerMethodField()
    provider = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'first_name', 'last_name', 
            'display_name', 'avatar_url', 'provider',
            'is_active', 'date_joined'
        ]
        read_only_fields = ['id', 'date_joined']
    
    def get_display_name(self, obj):
        """Get user's display name"""
        if hasattr(obj, 'technobits_profile'):
            return obj.technobits_profile.display_name
        return obj.get_full_name() or obj.first_name or obj.email.split('@')[0]
    
    def get_avatar_url(self, obj):
        """Get user's avatar URL"""
        if hasattr(obj, 'technobits_profile'):
            return obj.technobits_profile.avatar_url
        return ''
    
    def get_provider(self, obj):
        """Get user's auth provider"""
        if hasattr(obj, 'technobits_profile'):
            return obj.technobits_profile.provider
        return 'email'


class RegisterSerializer(serializers.Serializer):
    """Serializer for user registration"""
    
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=30, required=False, allow_blank=True)
    recaptcha_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    def validate_email(self, value):
        """Validate email is unique"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        is_strong, errors = PasswordHelper.is_password_strong(value)
        if not is_strong:
            raise serializers.ValidationError(errors)
        return value
    
    def validate(self, attrs):
        """Validate reCAPTCHA if provided"""
        recaptcha_token = attrs.get('recaptcha_token')
        
        if recaptcha_token:
            request = self.context.get('request')
            ip_address = RequestHelper.get_client_ip(request) if request else None
            
            recaptcha_service = RecaptchaService()
            is_valid, result = recaptcha_service.verify_token(recaptcha_token, 'signup', ip_address)
            
            if not is_valid:
                raise serializers.ValidationError({
                    'recaptcha_token': 'Security verification failed. Please try again.'
                })
        
        return attrs
    
    def create(self, validated_data):
        """Create a new user"""
        # Remove recaptcha_token from data
        validated_data.pop('recaptcha_token', None)
        
        # Handle name field
        name = validated_data.pop('name', '')
        if name and not validated_data.get('first_name'):
            name_parts = name.strip().split(' ', 1)
            validated_data['first_name'] = name_parts[0]
            if len(name_parts) > 1:
                validated_data['last_name'] = name_parts[1]
        
        # Create user with profile
        user = AuthService.create_user_with_profile(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    recaptcha_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    def validate(self, attrs):
        """Validate credentials and reCAPTCHA"""
        email = attrs.get('email')
        password = attrs.get('password')
        recaptcha_token = attrs.get('recaptcha_token')
        
        request = self.context.get('request')
        ip_address = RequestHelper.get_client_ip(request) if request else None
        user_agent = RequestHelper.get_user_agent(request) if request else None
        
        # Check rate limiting
        if AuthService.is_rate_limited(email=email, ip_address=ip_address):
            raise serializers.ValidationError(
                "Too many login attempts. Please try again later."
            )
        
        # Validate reCAPTCHA if provided
        if recaptcha_token:
            recaptcha_service = RecaptchaService()
            is_valid, result = recaptcha_service.verify_token(recaptcha_token, 'login', ip_address)
            
            if not is_valid:
                raise serializers.ValidationError({
                    'recaptcha_token': 'Security verification failed. Please try again.'
                })
        
        # Authenticate user
        success, user, message = AuthService.authenticate_user(
            email, password, ip_address, user_agent
        )
        
        if not success:
            raise serializers.ValidationError("Invalid email or password.")
        
        attrs['user'] = user
        return attrs


class GoogleLoginSerializer(serializers.Serializer):
    """Serializer for Google OAuth login"""
    
    credential = serializers.CharField(write_only=True)
    
    def validate_credential(self, value):
        """Validate Google credential"""
        try:
            from .utils import GoogleCredentialVerifier
            
            # Verify credential and get user info
            google_info = GoogleCredentialVerifier.verify_credential(value)
            
            # Get or create user
            user = GoogleCredentialVerifier.get_or_create_user_from_google(google_info)
            
            return {'user': user, 'google_info': google_info}
            
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        except Exception as e:
            logger.error(f"Google authentication error: {str(e)}")
            raise serializers.ValidationError("Google authentication failed")
    
    def validate(self, attrs):
        """Process validated credential"""
        credential_data = attrs['credential']
        attrs['user'] = credential_data['user']
        attrs['google_info'] = credential_data['google_info']
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer for forgot password request"""
    
    email = serializers.EmailField()
    recaptcha_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    def validate(self, attrs):
        """Validate reCAPTCHA if provided"""
        recaptcha_token = attrs.get('recaptcha_token')
        
        if recaptcha_token:
            request = self.context.get('request')
            ip_address = RequestHelper.get_client_ip(request) if request else None
            
            recaptcha_service = RecaptchaService()
            is_valid, result = recaptcha_service.verify_token(recaptcha_token, 'forgot_password', ip_address)
            
            if not is_valid:
                raise serializers.ValidationError({
                    'recaptcha_token': 'Security verification failed. Please try again.'
                })
        
        return attrs


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer for password reset"""
    
    token = serializers.CharField()
    password = serializers.CharField(min_length=8, write_only=True)
    recaptcha_token = serializers.CharField(required=False, allow_blank=True, write_only=True)
    
    def validate_password(self, value):
        """Validate password strength"""
        is_strong, errors = PasswordHelper.is_password_strong(value)
        if not is_strong:
            raise serializers.ValidationError(errors)
        return value
    
    def validate_token(self, value):
        """Validate reset token"""
        is_valid, user = PasswordHelper.verify_reset_token(value)
        if not is_valid:
            raise serializers.ValidationError("Invalid or expired reset token.")
        return {'token': value, 'user': user}
    
    def validate(self, attrs):
        """Validate reCAPTCHA and process token"""
        recaptcha_token = attrs.get('recaptcha_token')
        
        # Validate reCAPTCHA if provided
        if recaptcha_token:
            request = self.context.get('request')
            ip_address = RequestHelper.get_client_ip(request) if request else None
            
            recaptcha_service = RecaptchaService()
            is_valid, result = recaptcha_service.verify_token(recaptcha_token, 'reset_password', ip_address)
            
            if not is_valid:
                raise serializers.ValidationError({
                    'recaptcha_token': 'Security verification failed. Please try again.'
                })
        
        # Process token data
        token_data = attrs['token']
        attrs['user'] = token_data['user']
        attrs['token'] = token_data['token']
        
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(min_length=8, write_only=True)
    
    def validate_current_password(self, value):
        """Validate current password"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        is_strong, errors = PasswordHelper.is_password_strong(value)
        if not is_strong:
            raise serializers.ValidationError(errors)
        return value
    
    def save(self):
        """Change user password"""
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        user.save()
        return user

