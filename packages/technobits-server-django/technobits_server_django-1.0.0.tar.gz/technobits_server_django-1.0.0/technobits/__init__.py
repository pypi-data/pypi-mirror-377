"""
Technobits Server Django Package
Modular integration library for Django applications
"""

__version__ = "1.0.0"
__author__ = "Technobits"

# Import main modules for easy access
# Note: Modules are imported lazily to avoid circular import issues
# These are commented out to prevent circular imports during Django startup
# The modules are still available via direct import
# from . import auth
# from . import payments  
# from . import email
# from . import utils

__all__ = ["auth", "payments", "email", "utils"]

