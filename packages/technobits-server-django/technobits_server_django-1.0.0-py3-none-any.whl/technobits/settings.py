"""
Default settings for Technobits Library
These can be overridden in your main Django settings
"""

from django.conf import settings

# Authentication settings
TECHNOBITS_AUTH_SETTINGS = {
    # Cookie settings
    'COOKIE_MAX_AGE': getattr(settings, 'TECHNOBITS_COOKIE_MAX_AGE', 60 * 60 * 24 * 7),  # 7 days
    'COOKIE_SECURE': getattr(settings, 'TECHNOBITS_COOKIE_SECURE', not settings.DEBUG),
    'COOKIE_SAMESITE': getattr(settings, 'TECHNOBITS_COOKIE_SAMESITE', 'Lax'),
    'COOKIE_DOMAIN': getattr(settings, 'TECHNOBITS_COOKIE_DOMAIN', None),
    
    # Token lifetimes
    'ACCESS_TOKEN_LIFETIME': getattr(settings, 'TECHNOBITS_ACCESS_TOKEN_LIFETIME', 60 * 15),  # 15 minutes
    'REFRESH_TOKEN_LIFETIME': getattr(settings, 'TECHNOBITS_REFRESH_TOKEN_LIFETIME', 60 * 60 * 24 * 7),  # 7 days
    
    # Rate limiting
    'MAX_LOGIN_ATTEMPTS': getattr(settings, 'TECHNOBITS_MAX_LOGIN_ATTEMPTS', 5),
    
    # Password requirements
    'PASSWORD_MIN_LENGTH': getattr(settings, 'TECHNOBITS_PASSWORD_MIN_LENGTH', 8),
    'PASSWORD_REQUIRE_UPPERCASE': getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_UPPERCASE', True),
    'PASSWORD_REQUIRE_LOWERCASE': getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_LOWERCASE', True),
    'PASSWORD_REQUIRE_DIGIT': getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_DIGIT', True),
    'PASSWORD_REQUIRE_SPECIAL': getattr(settings, 'TECHNOBITS_PASSWORD_REQUIRE_SPECIAL', False),
    
    # Frontend URL for password reset emails
    'FRONTEND_URL': getattr(settings, 'TECHNOBITS_FRONTEND_URL', 'http://localhost:3000'),
}

# Payment settings
TECHNOBITS_PAYMENTS_SETTINGS = {
    # Default currency
    'DEFAULT_CURRENCY': getattr(settings, 'TECHNOBITS_DEFAULT_CURRENCY', 'USD'),
    
    # Supported currencies
    'SUPPORTED_CURRENCIES': getattr(settings, 'TECHNOBITS_SUPPORTED_CURRENCIES', [
        'USD', 'EUR', 'GBP', 'CAD', 'AUD', 'INR'
    ]),
    
    # Transaction limits
    'MIN_TRANSACTION_AMOUNT': getattr(settings, 'TECHNOBITS_MIN_TRANSACTION_AMOUNT', 0.50),
    'MAX_TRANSACTION_AMOUNT': getattr(settings, 'TECHNOBITS_MAX_TRANSACTION_AMOUNT', 10000.00),
}

# Email settings
TECHNOBITS_EMAIL_SETTINGS = {
    # Email templates directory
    'TEMPLATES_DIR': getattr(settings, 'TECHNOBITS_EMAIL_TEMPLATES_DIR', 'technobits/email/templates'),
    
    # From email
    'FROM_EMAIL': getattr(settings, 'TECHNOBITS_FROM_EMAIL', settings.DEFAULT_FROM_EMAIL),
    'FROM_NAME': getattr(settings, 'TECHNOBITS_FROM_NAME', 'Technobits'),
}

# reCAPTCHA settings
TECHNOBITS_RECAPTCHA_SETTINGS = {
    'MIN_SCORE': getattr(settings, 'RECAPTCHA_MIN_SCORE', 0.5),
    'VERIFY_URL': 'https://www.google.com/recaptcha/api/siteverify',
}

# Required Django settings for Technobits
REQUIRED_SETTINGS = [
    'SECRET_KEY',
    'DEBUG',
    'ALLOWED_HOSTS',
]

# Recommended Django settings
RECOMMENDED_SETTINGS = {
    'CORS_ALLOW_CREDENTIALS': True,
    'CORS_ALLOWED_ORIGINS': [
        'http://localhost:3000',
        'http://localhost:3007',
    ],
}

def validate_settings():
    """
    Validate that required settings are present
    """
    missing_settings = []
    
    for setting in REQUIRED_SETTINGS:
        if not hasattr(settings, setting):
            missing_settings.append(setting)
    
    if missing_settings:
        raise ValueError(f"Missing required Django settings: {', '.join(missing_settings)}")
    
    # Check for OAuth settings if Google login is used
    if hasattr(settings, 'GOOGLE_OAUTH_CLIENT_ID') and not settings.GOOGLE_OAUTH_CLIENT_ID:
        print("Warning: GOOGLE_OAUTH_CLIENT_ID is empty - Google OAuth will be disabled")
    
    # Check for reCAPTCHA settings
    if hasattr(settings, 'RECAPTCHA_SECRET_KEY') and not settings.RECAPTCHA_SECRET_KEY:
        print("Warning: RECAPTCHA_SECRET_KEY is empty - reCAPTCHA verification will be disabled")
    
    return True


def get_technobits_settings():
    """
    Get all Technobits settings in one dictionary
    """
    return {
        'auth': TECHNOBITS_AUTH_SETTINGS,
        'payments': TECHNOBITS_PAYMENTS_SETTINGS,
        'email': TECHNOBITS_EMAIL_SETTINGS,
        'recaptcha': TECHNOBITS_RECAPTCHA_SETTINGS,
    }


