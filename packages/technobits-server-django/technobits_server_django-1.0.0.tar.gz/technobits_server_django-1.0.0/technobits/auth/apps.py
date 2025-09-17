from django.apps import AppConfig


class TechnobitsAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'technobits.auth'
    label = 'technobits_auth'  # Unique label to avoid conflicts
    verbose_name = 'Technobits Authentication'
    
    def ready(self):
        # Import signal handlers if any
        pass

