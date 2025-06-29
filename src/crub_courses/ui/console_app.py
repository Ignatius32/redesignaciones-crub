"""
CRUB Course Team Console Viewer

A simple command-line application for viewing and filtering course teams.
This provides a text-based interface for exploring course data.

Run with: python course_console_viewer.py
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from typing import List, Dict, Any, Optional
from collections import defaultdict, Counter

from crub_courses.api.factory import create_google_sheets_client, create_huayca_client
from crub_courses.services.course_team_service import CourseTeamService
from crub_courses.models.core import Course, AcademicPeriod, FacultyRole


class CourseConsoleViewer:
    """Console-based course viewer application"""
    
    def __init__(self):
        self.courses: List[Course] = []
        self.service: Optional[CourseTeamService] = None
        self.departments: List[str] = []
        
    def load_data(self):
        """Load course data from APIs"""
        print("🔄 Cargando datos desde las APIs...")
        
        try:
            # Initialize clients and service
            sheets_client = create_google_sheets_client()
            huayca_client = create_huayca_client()
            self.service = CourseTeamService(sheets_client, huayca_client)
            
            # Refresh data and detect courses
            status = self.service.refresh_data()
            self.courses = self.service.detect_unique_courses()
            
            # Get unique departments
            departments_set = set()
            for course in self.courses:
                if course.department:
                    departments_set.add(course.department)
            self.departments = sorted(list(departments_set))
            
            print(f"✅ Datos cargados exitosamente:")
            print(f"   - {len(self.courses)} cursos únicos")
            print(f"   - {len(self.departments)} departamentos")
            print(f"   - {status.materias_equipo_count} asignaciones")
            print(f"   - {status.designaciones_docentes_count} docentes")
            print(f"   - {status.huayca_materias_count} materias Huayca")
            print()
            
        except Exception as e:
            print(f"❌ Error cargando datos: {str(e)}")
            sys.exit(1)
    
    def display_main_menu(self):
        """Display the main menu options"""
        print("=" * 60)
        print("🎓 CRUB Course Team Viewer - Menú Principal")
        print("=" * 60)
        print("1. Ver todos los cursos")
        print("2. Filtrar por departamento")
        print("3. Buscar curso específico")
        print("4. Estadísticas generales")
        print("5. Ver departamentos disponibles")
        print("6. Actualizar datos")
        print("0. Salir")
        print("-" * 60)
    
    def display_courses(self, courses: List[Course], title: str = "Cursos"):
        """Display a list of courses in a formatted table"""
        if not courses:
            print("❌ No se encontraron cursos.")
            return
        
        print(f"\n📋 {title} ({len(courses)} encontrados)")
        print("-" * 120)
        print(f"{'Código':<8} {'Materia':<30} {'Período':<8} {'Carrera':<12} {'Departamento':<15} {'Equipo':<6} {'R/A'}")
        print("-" * 120)
        
        for course in courses:
            responsible_count = len(course.responsible_faculty)
            auxiliary_count = len(course.auxiliary_faculty)
            dept_name = course.department[:14] if course.department else "Sin datos"
            carrera_name = course.carrera[:11] if course.carrera else ""
            materia_name = course.materia[:29] if course.materia else ""
            
            print(f"{course.cod_siu:<8} {materia_name:<30} {course.periodo:<8} {carrera_name:<12} "
                  f"{dept_name:<15} {course.total_team_size:<6} {responsible_count}/{auxiliary_count}")
        
        print("-" * 120)
    
    def filter_by_department(self):
        """Filter courses by department"""
        if not self.departments:
            print("❌ No hay departamentos disponibles.")
            return
        
        print("\n🏢 Departamentos disponibles:")
        for i, dept in enumerate(self.departments, 1):
            # Count courses in this department
            course_count = sum(1 for course in self.courses 
                             if course.department == dept)
            print(f"{i:2d}. {dept} ({course_count} cursos)")
        
        try:
            choice = int(input(f"\nSeleccione departamento (1-{len(self.departments)}): "))
            if 1 <= choice <= len(self.departments):
                selected_dept = self.departments[choice - 1]
                filtered_courses = [
                    course for course in self.courses 
                    if course.department == selected_dept
                ]
                self.display_courses(filtered_courses, f"Cursos de {selected_dept}")
                
                # Show detailed view option
                if filtered_courses:
                    self.show_course_details_option(filtered_courses)
            else:
                print("❌ Opción inválida.")
        except ValueError:
            print("❌ Por favor ingrese un número válido.")
    
    def search_course(self):
        """Search for a specific course"""
        search_term = input("\n🔍 Ingrese código SIU o nombre de materia: ").strip().upper()
        
        if not search_term:
            print("❌ Debe ingresar un término de búsqueda.")
            return
        
        # Search by code or name
        found_courses = []
        for course in self.courses:
            if (search_term in course.cod_siu.upper() or 
                search_term in course.materia.upper()):
                found_courses.append(course)
        
        if found_courses:
            self.display_courses(found_courses, f"Resultados para '{search_term}'")
            self.show_course_details_option(found_courses)
        else:
            print(f"❌ No se encontraron cursos que coincidan con '{search_term}'.")
    
    def show_course_details_option(self, courses: List[Course]):
        """Show option to view detailed course information"""
        if not courses:
            return
        
        choice = input(f"\n¿Ver detalles de algún curso? (1-{len(courses)}, Enter para continuar): ").strip()
        
        if choice:
            try:
                index = int(choice) - 1
                if 0 <= index < len(courses):
                    self.display_course_details(courses[index])
                else:
                    print("❌ Número inválido.")
            except ValueError:
                print("❌ Por favor ingrese un número válido.")
    
    def display_course_details(self, course: Course):
        """Display detailed information about a specific course"""
        print(f"\n" + "=" * 80)
        print(f"📚 DETALLES DEL CURSO: {course.materia}")
        print("=" * 80)
        
        # Basic information
        print(f"🏷️  Código SIU: {course.cod_siu}")
        print(f"📅 Período: {course.periodo}")
        print(f"🎓 Carrera: {course.carrera}")
        print(f"🏢 Departamento: {course.department or 'Sin datos'}")
        print(f"📍 Área: {course.academic_area or 'Sin datos'}")
        print(f"📋 Optativa: {'Sí' if course.is_elective else 'No' if course.is_elective is not None else 'Sin datos'}")
        print(f"👥 Total Docentes: {course.total_team_size}")
        
        # Faculty details
        print(f"\n👨‍🏫 EQUIPO DOCENTE:")
        print("-" * 50)
        
        if course.responsible_faculty:
            print("📋 Responsables:")
            for member in course.responsible_faculty:
                dept_info = ""
                if member.personal_details:
                    dept_info = f" ({member.personal_details.departamento})"
                print(f"   • {member.docente}{dept_info}")
                print(f"     Legajo: {member.legajo}, Categoría: {member.categoria}")
        
        if course.auxiliary_faculty:
            print("\n🤝 Auxiliares:")
            for member in course.auxiliary_faculty:
                dept_info = ""
                if member.personal_details:
                    dept_info = f" ({member.personal_details.departamento})"
                print(f"   • {member.docente}{dept_info}")
                print(f"     Legajo: {member.legajo}, Categoría: {member.categoria}")
        
        # Huayca details
        if course.huayca_details:
            print(f"\n📊 INFORMACIÓN ACADÉMICA (Huayca):")
            print("-" * 50)
            print(f"Horas totales: {course.huayca_details.horas_totales}")
            print(f"Horas semanales: {course.huayca_details.horas_semanales}")
            print(f"Año del plan: {course.huayca_details.ano_plan}")
            if course.huayca_details.correlativas_para_cursar:
                print(f"Correlativas para cursar: {course.huayca_details.correlativas_para_cursar}")
        else:
            print(f"\n⚠️  Sin información académica detallada (Huayca)")
        
        print("=" * 80)
        input("\nPresione Enter para continuar...")
    
    def show_statistics(self):
        """Display general statistics"""
        print(f"\n📊 ESTADÍSTICAS GENERALES")
        print("=" * 50)
        
        # Basic counts
        print(f"📚 Total de cursos: {len(self.courses)}")
        print(f"🏢 Departamentos: {len(self.departments)}")
        
        # Period distribution
        period_counts = Counter(course.periodo for course in self.courses)
        print(f"\n📅 Distribución por período:")
        for period, count in period_counts.most_common():
            print(f"   {period}: {count} cursos")
        
        # Department distribution
        dept_counts = Counter(course.department for course in self.courses if course.department)
        print(f"\n🏢 Top 10 departamentos:")
        for dept, count in dept_counts.most_common(10):
            print(f"   {dept}: {count} cursos")
        
        # Team size distribution
        team_sizes = [course.total_team_size for course in self.courses]
        avg_team_size = sum(team_sizes) / len(team_sizes) if team_sizes else 0
        print(f"\n👥 Estadísticas de equipos:")
        print(f"   Tamaño promedio: {avg_team_size:.1f} docentes")
        print(f"   Tamaño mínimo: {min(team_sizes) if team_sizes else 0}")
        print(f"   Tamaño máximo: {max(team_sizes) if team_sizes else 0}")
        
        # Faculty role distribution
        total_responsible = sum(len(course.responsible_faculty) for course in self.courses)
        total_auxiliary = sum(len(course.auxiliary_faculty) for course in self.courses)
        print(f"   Total responsables: {total_responsible}")
        print(f"   Total auxiliares: {total_auxiliary}")
        
        # Data enrichment
        courses_with_huayca = sum(1 for course in self.courses if course.huayca_details)
        huayca_percentage = (courses_with_huayca / len(self.courses) * 100) if self.courses else 0
        print(f"\n📊 Calidad de datos:")
        print(f"   Cursos con datos Huayca: {courses_with_huayca} ({huayca_percentage:.1f}%)")
        
        print("=" * 50)
        input("\nPresione Enter para continuar...")
    
    def show_departments(self):
        """Display all available departments"""
        print(f"\n🏢 DEPARTAMENTOS DISPONIBLES ({len(self.departments)})")
        print("=" * 50)
        
        for i, dept in enumerate(self.departments, 1):
            course_count = sum(1 for course in self.courses 
                             if course.department == dept)
            print(f"{i:2d}. {dept} ({course_count} cursos)")
        
        print("=" * 50)
        input("\nPresione Enter para continuar...")
    
    def run(self):
        """Main application loop"""
        print("🎓 Bienvenido al CRUB Course Team Viewer")
        print("Cargando datos...")
        
        self.load_data()
        
        while True:
            self.display_main_menu()
            
            try:
                choice = input("Seleccione una opción: ").strip()
                
                if choice == "0":
                    print("👋 ¡Gracias por usar CRUB Course Team Viewer!")
                    break
                elif choice == "1":
                    self.display_courses(self.courses, "Todos los cursos")
                    self.show_course_details_option(self.courses)
                elif choice == "2":
                    self.filter_by_department()
                elif choice == "3":
                    self.search_course()
                elif choice == "4":
                    self.show_statistics()
                elif choice == "5":
                    self.show_departments()
                elif choice == "6":
                    self.load_data()
                else:
                    print("❌ Opción inválida. Por favor seleccione un número del 0 al 6.")
                
                if choice not in ["4", "5", "6"]:  # These already pause
                    input("\nPresione Enter para continuar...")
                
            except KeyboardInterrupt:
                print("\n\n👋 ¡Hasta luego!")
                break
            except Exception as e:
                print(f"❌ Error inesperado: {str(e)}")
                input("Presione Enter para continuar...")


if __name__ == "__main__":
    app = CourseConsoleViewer()
    app.run()
