"""
Quick integration test script for CRUB Course Team Management System.

This script performs a basic test of the entire pipeline:
1. Fetches data from all three sources
2. Runs the course detection algorithm
3. Displays summary statistics

Run with: python test_quick.py
"""

import sys
import logging
from datetime import datetime

from api_clients import create_google_sheets_client, create_huayca_client
from course_service import CourseTeamService
from models import FacultyRole

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run the quick integration test"""
    
    print("=" * 60)
    print("CRUB Course Team Management - Integration Test")
    print("=" * 60)
    print(f"Test started at: {datetime.now()}")
    print()
    
    try:
        # Step 1: Create API clients
        print("Step 1: Creating API clients...")
        sheets_client = create_google_sheets_client()
        huayca_client = create_huayca_client()
        print("✓ API clients created successfully")
        print()
        
        # Step 2: Create service and refresh data
        print("Step 2: Refreshing data from all sources...")
        service = CourseTeamService(sheets_client, huayca_client)
        
        status = service.refresh_data()
        print(f"✓ Data refresh completed:")
        print(f"  - Materias Equipo: {status.materias_equipo_count} records")
        print(f"  - Designaciones Docentes: {status.designaciones_docentes_count} records") 
        print(f"  - Huayca Materias: {status.huayca_materias_count} records")
        print(f"  - Faculty Match Rate: {status.faculty_match_rate:.1f}%")
        print(f"  - Huayca Match Rate: {status.huayca_match_rate:.1f}%")
        print()
        
        # Step 3: Detect unique courses
        print("Step 3: Running course detection algorithm...")
        courses = service.detect_unique_courses()
        print(f"✓ Course detection completed: {len(courses)} unique courses found")
        print()
        
        # Step 4: Analyze results
        print("Step 4: Analyzing results...")
        
        if courses:
            # Sample course analysis
            sample_course = courses[0]
            print(f"Sample Course:")
            print(f"  - Code: {sample_course.cod_siu}")
            print(f"  - Name: {sample_course.materia}")
            print(f"  - Period: {sample_course.periodo}")
            print(f"  - Career: {sample_course.carrera}")
            print(f"  - Team Size: {sample_course.total_team_size}")
            print(f"  - Responsible Faculty: {len(sample_course.responsible_faculty)}")
            print(f"  - Auxiliary Faculty: {len(sample_course.auxiliary_faculty)}")
            
            if sample_course.huayca_details:
                print(f"  - Department: {sample_course.department}")
                print(f"  - Academic Area: {sample_course.academic_area}")
                print(f"  - Is Elective: {sample_course.is_elective}")
            else:
                print(f"  - Huayca Details: Not available")
            
            print()
            
            # Team member analysis
            if sample_course.team_members:
                print("Sample Team Members:")
                for i, member in enumerate(sample_course.team_members[:3]):  # Show first 3
                    print(f"  {i+1}. {member.docente} ({member.rol.value})")
                    print(f"     Legajo: {member.legajo}")
                    if member.personal_details:
                        print(f"     Department: {member.personal_details.departamento}")
                        print(f"     Email: {member.personal_details.correos}")
                    else:
                        print(f"     Personal Details: Not available")
                    print()
        
        # Step 5: Generate summary
        print("Step 5: Generating summary statistics...")
        summary = service.generate_summary()
        
        print(f"Summary Statistics:")
        print(f"  - Total Courses: {summary.total_courses}")
        print(f"  - Total Assignments: {summary.total_assignments}")
        print(f"  - Unique Faculty: {summary.unique_faculty}")
        print(f"  - Faculty without Details: {summary.faculty_without_details}")
        print(f"  - Courses without Huayca Data: {summary.courses_without_huayca_data}")
        print()
        
        print("Courses by Department:")
        for dept, count in list(summary.courses_by_department.items())[:5]:
            print(f"  - {dept}: {count} courses")
        
        print()
        print("Courses by Period:")
        for period, count in summary.courses_by_period.items():
            print(f"  - {period}: {count} courses")
        
        print()
        print("Courses by Career:")
        for career, count in list(summary.courses_by_career.items())[:5]:
            print(f"  - {career}: {count} courses")
        
        print()
        
        # Step 6: Test search functionality
        print("Step 6: Testing search functionality...")
        
        if courses:
            # Test specific course lookup
            test_course = courses[0]
            found_course = service.get_course_by_code_and_period(
                test_course.cod_siu, 
                test_course.periodo
            )
            
            if found_course:
                print(f"✓ Course lookup successful: {found_course.cod_siu}")
            else:
                print("✗ Course lookup failed")
            
            # Test career search
            career_courses = service.get_courses_by_career(test_course.carrera)
            print(f"✓ Career search: {len(career_courses)} courses for '{test_course.carrera}'")
            
            # Test department search
            courses_with_dept = [c for c in courses if c.department]
            if courses_with_dept:
                test_dept = courses_with_dept[0].department
                dept_courses = service.get_courses_by_department(test_dept)
                print(f"✓ Department search: {len(dept_courses)} courses for '{test_dept}'")
        
        print()
        print("=" * 60)
        print("✓ INTEGRATION TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ INTEGRATION TEST FAILED!")
        print(f"Error: {str(e)}")
        print("=" * 60)
        logger.exception("Integration test failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
