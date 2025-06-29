"""
Core service for detecting course teams and aggregating data from multiple sources.

This service implements the main business logic for:
1. Detecting unique courses from materias_equipo data
2. Building course teams with faculty assignments
3. Enriching data from designaciones_docentes and Huayca APIs
"""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
import logging

from ..models.core import (
    Course, TeamMember, FacultyDetails, HuaycaCourseDetails,
    AcademicPeriod
)
from ..models.summary import CourseTeamSummary, DataSourceStatus
from ..api.clients import GoogleSheetsClient, HuaycaClient

logger = logging.getLogger(__name__)


class CourseTeamService:
    """Main service for course team detection and data aggregation"""
    
    def __init__(self, sheets_client: GoogleSheetsClient, huayca_client: HuaycaClient):
        """Initialize the service with API clients"""
        self.sheets_client = sheets_client
        self.huayca_client = huayca_client
        
        # Cache for data
        self._materias_equipo_cache: Optional[List[Dict[str, Any]]] = None
        self._designaciones_cache: Optional[List[Dict[str, Any]]] = None
        self._huayca_cache: Optional[List[Dict[str, Any]]] = None
    
    def refresh_data(self) -> DataSourceStatus:
        """
        Refresh all data from external sources and return status.
        """
        logger.info("Refreshing data from all sources")
        
        try:
            # Fetch data from all sources
            self._materias_equipo_cache = self.sheets_client.get_materias_equipo()
            self._designaciones_cache = self.sheets_client.get_designaciones_docentes()
            self._huayca_cache = self.huayca_client.get_all_materias()
            
            # Calculate matching statistics
            faculty_match_rate = self._calculate_faculty_match_rate()
            huayca_match_rate = self._calculate_huayca_match_rate()
            
            status = DataSourceStatus(
                materias_equipo_count=len(self._materias_equipo_cache),
                designaciones_docentes_count=len(self._designaciones_cache),
                huayca_materias_count=len(self._huayca_cache),
                faculty_match_rate=faculty_match_rate,
                huayca_match_rate=huayca_match_rate,
                sync_errors=[]
            )
            
            logger.info(f"Data refresh completed: {status}")
            return status
            
        except Exception as e:
            logger.error(f"Error during data refresh: {str(e)}")
            raise
    
    def detect_unique_courses(self) -> List[Course]:
        """
        Detect unique courses and build complete course objects.
        
        Algorithm:
        1. Group materias_equipo by (Cod SIU, Período)
        2. Create Course objects with team members
        3. Enrich with faculty details from designaciones_docentes
        4. Enrich with course details from Huayca
        
        Returns:
            List of Course objects with complete data
        """
        if self._materias_equipo_cache is None:
            raise ValueError("Data not loaded. Call refresh_data() first.")
        
        logger.info("Starting course detection algorithm")
        
        # Step 1: Group assignments by unique course identifier
        course_groups = self._group_assignments_by_course()
        
        # Step 2: Build Course objects
        courses = self._build_course_objects(course_groups)
        
        # Step 3: Enrich with faculty details
        self._enrich_with_faculty_details(courses)
        
        # Step 4: Enrich with Huayca details
        self._enrich_with_huayca_details(courses)
        
        logger.info(f"Course detection completed: {len(courses)} unique courses found")
        return courses
    
    def _group_assignments_by_course(self) -> Dict[tuple, List[Dict[str, Any]]]:
        """Group materias_equipo records by (Cod SIU, Período)"""
        
        course_groups = defaultdict(list)
        
        for assignment in self._materias_equipo_cache:
            # Create unique key from Cod SIU and Período
            key = (assignment.get("Cod SIU", ""), assignment.get("Período", ""))
            course_groups[key].append(assignment)
        
        logger.info(f"Grouped {len(self._materias_equipo_cache)} assignments into {len(course_groups)} unique courses")
        return dict(course_groups)
    
    def _build_course_objects(self, course_groups: Dict[tuple, List[Dict[str, Any]]]) -> List[Course]:
        """Build Course objects from grouped assignments"""
        
        courses = []
        
        for (cod_siu, periodo), assignments in course_groups.items():
            if not cod_siu or not periodo:
                logger.warning(f"Skipping course with empty identifier: {cod_siu}, {periodo}")
                continue
            
            # Use first assignment for common course data
            first_assignment = assignments[0]
            
            # Create course object
            course = Course(
                cod_siu=cod_siu,
                materia=first_assignment.get("Materia", ""),
                periodo=AcademicPeriod(periodo) if periodo in AcademicPeriod.__members__.values() else periodo,
                carrera=first_assignment.get("Carrera", ""),
                team_members=[]
            )
            
            # Add all team members
            for assignment in assignments:
                try:
                    team_member = TeamMember(**assignment)
                    course.team_members.append(team_member)
                except Exception as e:
                    logger.warning(f"Error creating TeamMember from assignment {assignment.get('id_redesignacion')}: {str(e)}")
                    continue
            
            courses.append(course)
        
        return courses
    
    def _enrich_with_faculty_details(self, courses: List[Course]) -> None:
        """
        Enrich team members with personal details from designaciones_docentes.
        Matching: materias_equipo.Desig ↔ designaciones_docentes."D Desig"
        """
        if self._designaciones_cache is None:
            logger.warning("No designaciones_docentes data available for enrichment")
            return
        
        # Create lookup dictionary by D Desig
        faculty_lookup = {}
        for faculty_data in self._designaciones_cache:
            d_desig = faculty_data.get("D Desig", "")
            if d_desig:
                faculty_lookup[d_desig] = faculty_data
        
        logger.info(f"Created faculty lookup with {len(faculty_lookup)} records")
        
        # Enrich team members
        matched_count = 0
        for course in courses:
            for member in course.team_members:
                faculty_data = faculty_lookup.get(member.desig)
                if faculty_data:
                    try:
                        member.personal_details = FacultyDetails(**faculty_data)
                        matched_count += 1
                    except Exception as e:
                        logger.warning(f"Error creating FacultyDetails for {member.desig}: {str(e)}")
        
        total_members = sum(len(course.team_members) for course in courses)
        logger.info(f"Enriched {matched_count}/{total_members} team members with faculty details")
    
    def _enrich_with_huayca_details(self, courses: List[Course]) -> None:
        """
        Enrich courses with academic details from Huayca.
        Matching: materias_equipo."Cod SIU" ↔ huayca.cod_guarani
        """
        if self._huayca_cache is None:
            logger.warning("No Huayca data available for enrichment")
            return
        
        # Create lookup dictionary by cod_guarani
        huayca_lookup = {}
        for course_data in self._huayca_cache:
            cod_guarani = course_data.get("cod_guarani", "")
            if cod_guarani:
                huayca_lookup[cod_guarani] = course_data
        
        logger.info(f"Created Huayca lookup with {len(huayca_lookup)} records")
        
        # Enrich courses
        matched_count = 0
        for course in courses:
            huayca_data = huayca_lookup.get(course.cod_siu)
            if huayca_data:
                try:
                    course.huayca_details = HuaycaCourseDetails(**huayca_data)
                    matched_count += 1
                except Exception as e:
                    logger.warning(f"Error creating HuaycaCourseDetails for {course.cod_siu}: {str(e)}")
        
        logger.info(f"Enriched {matched_count}/{len(courses)} courses with Huayca details")
    
    def get_course_by_code_and_period(self, cod_siu: str, periodo: str) -> Optional[Course]:
        """Get a specific course by its code and period"""
        
        courses = self.detect_unique_courses()
        
        for course in courses:
            if course.cod_siu == cod_siu and course.periodo == periodo:
                return course
        
        return None
    
    def get_courses_by_department(self, department: str) -> List[Course]:
        """Get all courses for a specific department"""
        
        courses = self.detect_unique_courses()
        
        return [
            course for course in courses
            if course.department and course.department.upper() == department.upper()
        ]
    
    def get_courses_by_area(self, area: str) -> List[Course]:
        """Get all courses for a specific academic area"""
        
        courses = self.detect_unique_courses()
        
        return [
            course for course in courses
            if course.academic_area and course.academic_area.upper() == area.upper()
        ]
    
    def get_courses_by_career(self, career: str) -> List[Course]:
        """Get all courses for a specific career"""
        
        courses = self.detect_unique_courses()
        
        return [
            course for course in courses
            if course.carrera.upper() == career.upper()
        ]
    
    def generate_summary(self) -> CourseTeamSummary:
        """Generate summary statistics for course teams"""
        
        courses = self.detect_unique_courses()
        
        # Basic counts
        total_courses = len(courses)
        total_assignments = sum(len(course.team_members) for course in courses)
        
        # Unique faculty count
        unique_faculty: Set[str] = set()
        faculty_without_details = 0
        
        for course in courses:
            for member in course.team_members:
                unique_faculty.add(member.legajo)
                if member.personal_details is None:
                    faculty_without_details += 1
        
        # Courses without Huayca data
        courses_without_huayca_data = sum(
            1 for course in courses if course.huayca_details is None
        )
        
        # Group by various dimensions
        courses_by_department = defaultdict(int)
        courses_by_period = defaultdict(int)
        courses_by_career = defaultdict(int)
        
        for course in courses:
            # Department from Huayca data
            if course.department:
                courses_by_department[course.department] += 1
            
            # Period
            courses_by_period[course.periodo] += 1
            
            # Career
            courses_by_career[course.carrera] += 1
        
        return CourseTeamSummary(
            total_courses=total_courses,
            total_assignments=total_assignments,
            unique_faculty=len(unique_faculty),
            courses_by_department=dict(courses_by_department),
            courses_by_period=dict(courses_by_period),
            courses_by_career=dict(courses_by_career),
            faculty_without_details=faculty_without_details,
            courses_without_huayca_data=courses_without_huayca_data
        )
    
    def _calculate_faculty_match_rate(self) -> float:
        """Calculate percentage of assignments with faculty details"""
        if not self._materias_equipo_cache or not self._designaciones_cache:
            return 0.0
        
        # Create set of available D Desig values
        available_desigs = {
            item.get("D Desig", "") for item in self._designaciones_cache
        }
        
        # Count matches
        total_assignments = len(self._materias_equipo_cache)
        matched_assignments = sum(
            1 for assignment in self._materias_equipo_cache
            if assignment.get("Desig", "") in available_desigs
        )
        
        return (matched_assignments / total_assignments) * 100 if total_assignments > 0 else 0.0
    
    def _calculate_huayca_match_rate(self) -> float:
        """Calculate percentage of courses with Huayca details"""
        if not self._materias_equipo_cache or not self._huayca_cache:
            return 0.0
        
        # Create set of available id_materia values
        available_ids = {
            str(item.get("id_materia", "")) for item in self._huayca_cache
        }
        
        # Get unique course codes
        unique_codes = {
            assignment.get("Cod SIU", "") for assignment in self._materias_equipo_cache
        }
        
        # Count matches
        matched_codes = sum(
            1 for code in unique_codes
            if code in available_ids
        )
        
        return (matched_codes / len(unique_codes)) * 100 if unique_codes else 0.0
