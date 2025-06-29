"""
CRUB Course Team Management System

A system for detecting course teams and aggregating data from multiple sources:
- Google Sheets API (materias_equipo, designaciones_docentes)
- Huayca API (course information)

This package provides models, services, and applications for managing
and viewing course team assignments at CRUB.
"""

__version__ = "1.0.0"
__author__ = "CRUB Development Team"
__email__ = "dev@crub.uncoma.edu.ar"

from .models import Course, TeamMember, FacultyDetails, HuaycaCourseDetails
from .services import CourseTeamService
from .api import GoogleSheetsClient, HuaycaClient

__all__ = [
    "Course",
    "TeamMember", 
    "FacultyDetails",
    "HuaycaCourseDetails",
    "CourseTeamService",
    "GoogleSheetsClient",
    "HuaycaClient"
]
