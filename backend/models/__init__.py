# backend/models/__init__.py
from .base import Base
from .user import User
from .profile import LinkedInProfile

__all__ = ['Base', 'User', 'LinkedInProfile'] 