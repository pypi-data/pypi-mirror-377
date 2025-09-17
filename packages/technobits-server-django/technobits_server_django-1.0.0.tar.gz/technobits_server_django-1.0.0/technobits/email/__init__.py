"""
Technobits Email Module
Provides email service integration
"""

from .services import EmailService
from .apps import TechnobitsEmailConfig

__all__ = [
    "EmailService",
    "TechnobitsEmailConfig",
]


