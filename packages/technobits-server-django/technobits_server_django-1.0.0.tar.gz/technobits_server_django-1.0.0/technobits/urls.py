"""
Main URLs module for Technobits Library
"""

from django.urls import path, include


def include_technobits_urls(prefix='api/'):
    """
    Helper function to include all Technobits URLs with a common prefix
    
    Usage in main urls.py:
    from technobits.urls import include_technobits_urls
    
    urlpatterns = [
        # ... your existing URLs
    ] + include_technobits_urls()
    """
    return [
        path(f'{prefix}auth/', include('technobits.auth.urls')),
        path(f'{prefix}email/', include('technobits.email.urls')),
    ]


# Default URL patterns (can be included directly)
urlpatterns = [
    path('auth/', include('technobits.auth.urls')),
    path('email/', include('technobits.email.urls')),
]


