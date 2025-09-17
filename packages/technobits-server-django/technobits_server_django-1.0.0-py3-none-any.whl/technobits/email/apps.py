from django.apps import AppConfig


class TechnobitsEmailConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'technobits.email'
    label = 'technobits_email'  # Unique label to avoid conflicts
    verbose_name = 'Technobits Email'


