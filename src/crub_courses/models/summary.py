"""
Summary and status models for the CRUB system.

This module contains models for aggregated data and system status information.
"""

from typing import Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel


class CourseTeamSummary(BaseModel):
    """Summary statistics for course teams"""
    
    total_courses: int
    total_assignments: int
    unique_faculty: int
    courses_by_department: Dict[str, int]
    courses_by_period: Dict[str, int]
    courses_by_career: Dict[str, int]
    faculty_without_details: int
    courses_without_huayca_data: int


class DataSourceStatus(BaseModel):
    """Status of data sources and last sync information"""
    
    materias_equipo_count: int
    designaciones_docentes_count: int
    huayca_materias_count: int
    last_sync: Optional[datetime] = None
    sync_errors: List[str] = []
    
    # Matching statistics
    faculty_match_rate: float  # Percentage of assignments with faculty details
    huayca_match_rate: float   # Percentage of courses with Huayca details
