"""Data models for the CRUB system"""

from .core import (
    AcademicPeriod, FacultyRole, OptativeStatus,
    FacultyDetails, TeamMember, HuaycaCourseDetails, Course
)
from .summary import CourseTeamSummary, DataSourceStatus
from .types import MateriasEquipoRaw, DesignacionesDocentesRaw, HuaycaMateriasRaw

__all__ = [
    "AcademicPeriod",
    "FacultyRole", 
    "OptativeStatus",
    "FacultyDetails",
    "TeamMember",
    "HuaycaCourseDetails", 
    "Course",
    "CourseTeamSummary",
    "DataSourceStatus",
    "MateriasEquipoRaw",
    "DesignacionesDocentesRaw", 
    "HuaycaMateriasRaw"
]
