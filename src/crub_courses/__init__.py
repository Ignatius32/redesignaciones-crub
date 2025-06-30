"""
CRUB Course Team Management System

A FastAPI application for managing faculty designations and course assignments,
combining data from multiple sources:
- Google Sheets API (materias_equipo, designaciones_docentes)  
- Huayca API (detailed course information)

This package provides models, services, and a REST API for managing
and viewing faculty designations and course assignments at CRUB.
"""

__version__ = "1.0.0"
__author__ = "CRUB Development Team"
__email__ = "dev@crub.uncoma.edu.ar"

# Import main components
from .api import GoogleSheetsClient, HuaycaClient
from .services.designaciones import DesignacionesService

__all__ = [
    "GoogleSheetsClient",
    "HuaycaClient", 
    "DesignacionesService"
]
