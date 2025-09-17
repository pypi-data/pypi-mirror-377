"""
Authentication Admin for Technobits Library
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, LoginAttempt, PasswordResetToken


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Technobits Profile'
    fields = ['provider', 'google_id', 'avatar_url', 'phone', 'timezone', 
              'email_notifications', 'marketing_emails', 'last_login_ip']
    readonly_fields = ['last_login_ip']


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = BaseUserAdmin.list_display + ('get_provider', 'get_last_login_ip')
    list_filter = BaseUserAdmin.list_filter + ('technobits_profile__provider',)
    
    def get_provider(self, obj):
        if hasattr(obj, 'technobits_profile'):
            return obj.technobits_profile.provider
        return 'N/A'
    get_provider.short_description = 'Provider'
    
    def get_last_login_ip(self, obj):
        if hasattr(obj, 'technobits_profile'):
            return obj.technobits_profile.last_login_ip
        return 'N/A'
    get_last_login_ip.short_description = 'Last Login IP'


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'provider', 'google_id', 'created_at', 'last_login_ip']
    list_filter = ['provider', 'email_notifications', 'marketing_emails', 'created_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name', 'google_id']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'provider', 'google_id', 'avatar_url')
        }),
        ('Contact Info', {
            'fields': ('phone', 'timezone')
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'marketing_emails')
        }),
        ('Metadata', {
            'fields': ('last_login_ip', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = ['email', 'ip_address', 'success', 'failure_reason', 'timestamp']
    list_filter = ['success', 'failure_reason', 'timestamp']
    search_fields = ['email', 'ip_address']
    readonly_fields = ['timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False


@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token_preview', 'created_at', 'used_at', 'is_expired']
    list_filter = ['created_at', 'used_at']
    search_fields = ['user__email', 'token']
    readonly_fields = ['created_at', 'is_expired', 'is_used']
    
    def token_preview(self, obj):
        return f"{obj.token[:10]}..."
    token_preview.short_description = 'Token'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

