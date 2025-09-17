"""
Authentication Models for Technobits Library
"""

from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Extended user profile model
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='technobits_profile')
    
    # OAuth provider info
    google_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    provider = models.CharField(max_length=20, blank=True, default='email')  # 'email', 'google'
    
    # Additional profile info
    avatar_url = models.URLField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    marketing_emails = models.BooleanField(default=False)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        db_table = 'technobits_user_profile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        
    def __str__(self):
        return f"{self.user.email} - {self.provider}"
    
    @property
    def display_name(self):
        """Get user's display name"""
        return self.user.get_full_name() or self.user.first_name or self.user.email.split('@')[0]


class LoginAttempt(models.Model):
    """
    Track login attempts for security
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    success = models.BooleanField(default=False)
    failure_reason = models.CharField(max_length=100, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'technobits_login_attempt'
        verbose_name = 'Login Attempt'
        verbose_name_plural = 'Login Attempts'
        indexes = [
            models.Index(fields=['email', 'timestamp']),
            models.Index(fields=['ip_address', 'timestamp']),
        ]
        
    def __str__(self):
        status = "Success" if self.success else f"Failed ({self.failure_reason})"
        return f"{self.email} - {status} - {self.timestamp}"


class PasswordResetToken(models.Model):
    """
    Track password reset tokens
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='technobits_reset_tokens')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        db_table = 'technobits_password_reset_token'
        verbose_name = 'Password Reset Token'
        verbose_name_plural = 'Password Reset Tokens'
        
    def __str__(self):
        return f"{self.user.email} - {self.token[:10]}... - {self.created_at}"
    
    @property
    def is_expired(self):
        """Check if token is expired (24 hours)"""
        from django.utils import timezone
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    @property
    def is_used(self):
        """Check if token has been used"""
        return self.used_at is not None

