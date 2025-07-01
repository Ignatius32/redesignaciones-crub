"""
Service layer for business logic and data processing.

This module contains services that combine data from multiple APIs
and provide high-level business operations.
"""

from .designaciones import DesignacionesService

__all__ = [
    "DesignacionesService"
]
