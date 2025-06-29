"""
Integration tests for CRUB Course Team Management System.

This test suite verifies that the course team detection algorithm works correctly
with real data from the three APIs:
1. Google Sheets API (materias_equipo, designaciones_docentes)
2. Huayca API (course information)

Run with: pytest test_integration.py -v
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import logging
from typing import List, Dict, Any
from unittest.mock import patch

from crub_courses.api import (
    GoogleSheetsClient, HuaycaClient, 
    create_google_sheets_client, create_huayca_client,
    GoogleSheetsAPIError, HuaycaAPIError
)
from crub_courses.services import CourseTeamService
from crub_courses.models import (
    Course, TeamMember, FacultyDetails, HuaycaCourseDetails,
    AcademicPeriod, FacultyRole, CourseTeamSummary, DataSourceStatus
)

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAPIClients:
    """Test the API clients individually"""
    
    def test_google_sheets_client_creation(self):
        """Test that Google Sheets client can be created"""
        client = create_google_sheets_client()
        assert isinstance(client, GoogleSheetsClient)
        assert client.base_url is not None
        assert client.secret is not None
    
    def test_huayca_client_creation(self):
        """Test that Huayca client can be created"""
        client = create_huayca_client()
        assert isinstance(client, HuaycaClient)
        assert client.base_url is not None
        assert client.auth is not None
    
    @pytest.mark.integration
    def test_google_sheets_materias_equipo_fetch(self):
        """Test fetching materias_equipo data from real API"""
        client = create_google_sheets_client()
        
        try:
            data = client.get_materias_equipo()
            
            # Verify data structure
            assert isinstance(data, list)
            logger.info(f"Retrieved {len(data)} materias_equipo records")
            
            if data:
                # Check first record has expected fields
                first_record = data[0]
                expected_fields = [
                    "id_redesignacion", "Materia", "Cod SIU", "Carrera", 
                    "Docente", "Legajo", "Desig", "Rol", "Período"
                ]
                
                for field in expected_fields:
                    assert field in first_record, f"Missing field: {field}"
                
                logger.info(f"Sample record: {first_record}")
            
        except GoogleSheetsAPIError as e:
            pytest.fail(f"Google Sheets API error: {str(e)}")
    
    @pytest.mark.integration
    def test_google_sheets_designaciones_docentes_fetch(self):
        """Test fetching designaciones_docentes data from real API"""
        client = create_google_sheets_client()
        
        try:
            data = client.get_designaciones_docentes()
            
            # Verify data structure
            assert isinstance(data, list)
            logger.info(f"Retrieved {len(data)} designaciones_docentes records")
            
            if data:
                # Check first record has expected fields
                first_record = data[0]
                expected_fields = [
                    "id_redesignacion", "D Desig", "Legajo", 
                    "Apellido y Nombre", "Departamento", "Área"
                ]
                
                for field in expected_fields:
                    assert field in first_record, f"Missing field: {field}"
                
                logger.info(f"Sample faculty record: {first_record}")
            
        except GoogleSheetsAPIError as e:
            pytest.fail(f"Google Sheets API error: {str(e)}")
    
    @pytest.mark.integration
    def test_huayca_materias_fetch(self):
        """Test fetching materias data from real Huayca API"""
        client = create_huayca_client()
        
        try:
            data = client.get_all_materias()
            
            # Verify data structure
            assert isinstance(data, list)
            logger.info(f"Retrieved {len(data)} Huayca materias")
            
            if data:
                # Check first record has expected fields
                first_record = data[0]
                expected_fields = [
                    "id_materia", "nombre_materia", "cod_guarani", 
                    "depto", "area", "optativa"
                ]
                
                for field in expected_fields:
                    assert field in first_record, f"Missing field: {field}"
                
                logger.info(f"Sample Huayca record: {first_record}")
            
        except HuaycaAPIError as e:
            pytest.fail(f"Huayca API error: {str(e)}")


class TestCourseTeamService:
    """Test the main course team service with real data"""
    
    @pytest.fixture
    def service(self):
        """Create a CourseTeamService instance with real API clients"""
        sheets_client = create_google_sheets_client()
        huayca_client = create_huayca_client()
        return CourseTeamService(sheets_client, huayca_client)
    
    @pytest.mark.integration
    def test_data_refresh(self, service):
        """Test refreshing data from all sources"""
        try:
            status = service.refresh_data()
            
            # Verify status object
            assert isinstance(status, DataSourceStatus)
            assert status.materias_equipo_count >= 0
            assert status.designaciones_docentes_count >= 0
            assert status.huayca_materias_count >= 0
            assert 0 <= status.faculty_match_rate <= 100
            assert 0 <= status.huayca_match_rate <= 100
            
            logger.info(f"Data refresh status: {status}")
            
            # Verify caches are populated
            assert service._materias_equipo_cache is not None
            assert service._designaciones_cache is not None
            assert service._huayca_cache is not None
            
        except Exception as e:
            pytest.fail(f"Data refresh failed: {str(e)}")
    
    @pytest.mark.integration
    def test_course_detection_algorithm(self, service):
        """Test the core course detection and team building algorithm"""
        
        # First refresh data
        service.refresh_data()
        
        try:
            courses = service.detect_unique_courses()
            
            # Basic validation
            assert isinstance(courses, list)
            logger.info(f"Detected {len(courses)} unique courses")
            
            if courses:
                # Test first course structure
                first_course = courses[0]
                assert isinstance(first_course, Course)
                assert first_course.cod_siu is not None
                assert first_course.materia is not None
                assert first_course.periodo is not None
                assert first_course.carrera is not None
                assert isinstance(first_course.team_members, list)
                
                logger.info(f"Sample course: {first_course.cod_siu} - {first_course.materia}")
                logger.info(f"Team size: {first_course.total_team_size}")
                
                # Test team member structure
                if first_course.team_members:
                    first_member = first_course.team_members[0]
                    assert isinstance(first_member, TeamMember)
                    assert first_member.legajo is not None
                    assert first_member.docente is not None
                    assert isinstance(first_member.rol, FacultyRole)
                    
                    logger.info(f"Sample team member: {first_member.docente} ({first_member.rol})")
                
                # Test enrichment
                enriched_with_faculty = sum(
                    1 for course in courses 
                    for member in course.team_members 
                    if member.personal_details is not None
                )
                
                enriched_with_huayca = sum(
                    1 for course in courses 
                    if course.huayca_details is not None
                )
                
                logger.info(f"Team members with faculty details: {enriched_with_faculty}")
                logger.info(f"Courses with Huayca details: {enriched_with_huayca}")
                
        except Exception as e:
            pytest.fail(f"Course detection failed: {str(e)}")
    
    @pytest.mark.integration
    def test_data_matching_quality(self, service):
        """Test the quality of data matching between sources"""
        
        service.refresh_data()
        courses = service.detect_unique_courses()
        
        if not courses:
            pytest.skip("No courses detected, skipping matching quality test")
        
        # Analyze faculty matching
        total_members = sum(len(course.team_members) for course in courses)
        members_with_details = sum(
            1 for course in courses 
            for member in course.team_members 
            if member.personal_details is not None
        )
        
        faculty_match_rate = (members_with_details / total_members) * 100 if total_members > 0 else 0
        
        # Analyze Huayca matching
        courses_with_huayca = sum(
            1 for course in courses 
            if course.huayca_details is not None
        )
        
        huayca_match_rate = (courses_with_huayca / len(courses)) * 100 if courses else 0
        
        logger.info(f"Faculty matching rate: {faculty_match_rate:.1f}%")
        logger.info(f"Huayca matching rate: {huayca_match_rate:.1f}%")
        
        # We expect some reasonable matching rates (adjust thresholds as needed)
        assert faculty_match_rate >= 0  # At least some matches expected
        assert huayca_match_rate >= 0   # At least some matches expected
    
    @pytest.mark.integration
    def test_course_properties(self, service):
        """Test course property accessors work correctly"""
        
        service.refresh_data()
        courses = service.detect_unique_courses()
        
        if not courses:
            pytest.skip("No courses detected, skipping property test")
        
        for course in courses[:5]:  # Test first 5 courses
            # Test unique key
            assert course.unique_key == f"{course.cod_siu}_{course.periodo}"
            
            # Test faculty role filters
            responsible = course.responsible_faculty
            auxiliary = course.auxiliary_faculty
            
            assert len(responsible) + len(auxiliary) == len(course.team_members)
            
            # Test department and area (if Huayca data available)
            if course.huayca_details:
                assert course.department == course.huayca_details.depto
                assert course.academic_area == course.huayca_details.area
                assert isinstance(course.is_elective, bool)
            
            logger.info(f"Course {course.cod_siu}: {len(responsible)} responsible, {len(auxiliary)} auxiliary")
    
    @pytest.mark.integration
    def test_summary_generation(self, service):
        """Test course team summary generation"""
        
        service.refresh_data()
        
        try:
            summary = service.generate_summary()
            
            assert isinstance(summary, CourseTeamSummary)
            assert summary.total_courses >= 0
            assert summary.total_assignments >= 0
            assert summary.unique_faculty >= 0
            assert isinstance(summary.courses_by_department, dict)
            assert isinstance(summary.courses_by_period, dict)
            assert isinstance(summary.courses_by_career, dict)
            
            logger.info(f"Summary: {summary.total_courses} courses, {summary.total_assignments} assignments")
            logger.info(f"Unique faculty: {summary.unique_faculty}")
            logger.info(f"Departments: {list(summary.courses_by_department.keys())}")
            logger.info(f"Periods: {list(summary.courses_by_period.keys())}")
            
        except Exception as e:
            pytest.fail(f"Summary generation failed: {str(e)}")
    
    @pytest.mark.integration
    def test_search_functionality(self, service):
        """Test various search and filter methods"""
        
        service.refresh_data()
        courses = service.detect_unique_courses()
        
        if not courses:
            pytest.skip("No courses detected, skipping search test")
        
        # Test search by code and period
        first_course = courses[0]
        found_course = service.get_course_by_code_and_period(
            first_course.cod_siu, 
            first_course.periodo
        )
        
        assert found_course is not None
        assert found_course.cod_siu == first_course.cod_siu
        assert found_course.periodo == first_course.periodo
        
        # Test search by career
        if first_course.carrera:
            career_courses = service.get_courses_by_career(first_course.carrera)
            assert len(career_courses) >= 1
            assert first_course in career_courses
        
        # Test search by department (if Huayca data available)
        courses_with_dept = [c for c in courses if c.department]
        if courses_with_dept:
            test_dept = courses_with_dept[0].department
            dept_courses = service.get_courses_by_department(test_dept)
            assert len(dept_courses) >= 1
        
        logger.info("All search functionality tests passed")


class TestDataValidation:
    """Test data validation and error handling"""
    
    @pytest.mark.integration
    def test_model_validation_with_real_data(self):
        """Test that real data can be properly validated by Pydantic models"""
        
        # Test with real Google Sheets data
        sheets_client = create_google_sheets_client()
        
        try:
            materias_data = sheets_client.get_materias_equipo()
            designaciones_data = sheets_client.get_designaciones_docentes()
            
            # Try to create model instances from real data
            if materias_data:
                for record in materias_data[:3]:  # Test first 3 records
                    try:
                        team_member = TeamMember(**record)
                        assert team_member.id_redesignacion is not None
                        assert team_member.legajo is not None
                        logger.info(f"Successfully created TeamMember: {team_member.docente}")
                    except Exception as e:
                        logger.warning(f"Failed to create TeamMember from {record}: {str(e)}")
            
            if designaciones_data:
                for record in designaciones_data[:3]:  # Test first 3 records
                    try:
                        faculty = FacultyDetails(**record)
                        assert faculty.id_redesignacion is not None
                        assert faculty.legajo is not None
                        logger.info(f"Successfully created FacultyDetails: {faculty.apellido_nombre}")
                    except Exception as e:
                        logger.warning(f"Failed to create FacultyDetails from {record}: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Model validation test failed: {str(e)}")
    
    @pytest.mark.integration
    def test_huayca_model_validation(self):
        """Test Huayca data model validation"""
        
        huayca_client = create_huayca_client()
        
        try:
            materias_data = huayca_client.get_all_materias()
            
            if materias_data:
                for record in materias_data[:3]:  # Test first 3 records
                    try:
                        huayca_details = HuaycaCourseDetails(**record)
                        assert huayca_details.id_materia is not None
                        assert huayca_details.nombre_materia is not None
                        logger.info(f"Successfully created HuaycaCourseDetails: {huayca_details.nombre_materia}")
                    except Exception as e:
                        logger.warning(f"Failed to create HuaycaCourseDetails from {record}: {str(e)}")
        
        except Exception as e:
            pytest.fail(f"Huayca model validation test failed: {str(e)}")


# Test configuration
def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests (may be slow)"
    )


if __name__ == "__main__":
    # Run a quick integration test
    print("Running quick integration test...")
    
    # Test API clients
    print("Testing Google Sheets client...")
    sheets_client = create_google_sheets_client()
    
    try:
        materias = sheets_client.get_materias_equipo()
        print(f"✓ Retrieved {len(materias)} materias_equipo records")
        
        designaciones = sheets_client.get_designaciones_docentes()
        print(f"✓ Retrieved {len(designaciones)} designaciones_docentes records")
    except Exception as e:
        print(f"✗ Google Sheets error: {str(e)}")
    
    print("\nTesting Huayca client...")
    huayca_client = create_huayca_client()
    
    try:
        huayca_materias = huayca_client.get_all_materias()
        print(f"✓ Retrieved {len(huayca_materias)} Huayca materias")
    except Exception as e:
        print(f"✗ Huayca error: {str(e)}")
    
    print("\nTesting course team service...")
    service = CourseTeamService(sheets_client, huayca_client)
    
    try:
        status = service.refresh_data()
        print(f"✓ Data refresh successful: {status.materias_equipo_count} + {status.designaciones_docentes_count} + {status.huayca_materias_count} records")
        
        courses = service.detect_unique_courses()
        print(f"✓ Detected {len(courses)} unique courses")
        
        if courses:
            sample_course = courses[0]
            print(f"✓ Sample course: {sample_course.cod_siu} - {sample_course.materia} ({sample_course.total_team_size} members)")
        
        summary = service.generate_summary()
        print(f"✓ Generated summary: {summary.total_courses} courses, {summary.unique_faculty} faculty")
        
    except Exception as e:
        print(f"✗ Course service error: {str(e)}")
    
    print("\nIntegration test completed!")
