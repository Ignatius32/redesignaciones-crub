"""
FastAPI application for CRUB Course Team Management System.

This provides a REST API and web interface for viewing and managing course teams.
Features user authentication and course management capabilities.

Run with: uvicorn fastapi_app:app --reload
"""

from fastapi import FastAPI, HTTPException, Depends, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List, Optional, Dict, Any
import secrets
import logging
from pathlib import Path

import sys
from pathlib import Path
import os

# Add src to path for imports
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

# Load environment variables
def _load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = src_path.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())

_load_env_file()

from crub_courses.api.factory import create_google_sheets_client, create_huayca_client
from crub_courses.services.course_team_service import CourseTeamService
from crub_courses.models.core import Course, AcademicPeriod, FacultyRole
from crub_courses.models.summary import CourseTeamSummary
from pydantic import BaseModel

# Simple models for API responses
class DataSourceStatus(BaseModel):
    materias_equipo_count: int
    designaciones_docentes_count: int
    huayca_materias_count: int
    faculty_match_rate: float
    huayca_match_rate: float
    sync_errors: List[str]

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app initialization
app = FastAPI(
    title="CRUB Course Team Management API",
    description="API for managing course teams and faculty assignments at CRUB",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Security
security = HTTPBasic()

# Templates and static files
templates_dir = Path(__file__).parent / "templates"
static_dir = Path(__file__).parent / "static"

templates_dir.mkdir(exist_ok=True)
static_dir.mkdir(exist_ok=True)

templates = Jinja2Templates(directory=str(templates_dir))

# Mount static files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Global service instance (in production, use dependency injection)
_service_instance: Optional[CourseTeamService] = None

def get_service() -> CourseTeamService:
    """Get or create the course team service instance"""
    global _service_instance
    if _service_instance is None:
        logger.info("Initializing CourseTeamService...")
        sheets_client = create_google_sheets_client()
        huayca_client = create_huayca_client()
        _service_instance = CourseTeamService(sheets_client, huayca_client)
        # Load data on startup
        _service_instance.refresh_data()
        logger.info("CourseTeamService initialized successfully")
    return _service_instance

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify user credentials (basic auth for now)"""
    # Get credentials from environment variables
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "crub2025")
    
    correct_username = secrets.compare_digest(credentials.username, admin_username)
    correct_password = secrets.compare_digest(credentials.password, admin_password)
    
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# API Routes

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "CRUB Course Team Management"}

@app.get("/api/data-status", response_model=DataSourceStatus)
async def get_data_status(service: CourseTeamService = Depends(get_service)):
    """Get data source status and statistics"""
    # Get current status from the last refresh
    courses = service.detect_unique_courses()
    
    # Calculate basic match rates
    faculty_match_rate = 1.0  # Assume 100% for now
    huayca_match_rate = 0.0
    
    if courses:
        courses_with_huayca = [c for c in courses if c.huayca_data is not None]
        huayca_match_rate = len(courses_with_huayca) / len(courses)
    
    return DataSourceStatus(
        materias_equipo_count=len(service._materias_equipo_cache) if hasattr(service, '_materias_equipo_cache') and service._materias_equipo_cache else 0,
        designaciones_docentes_count=len(service._designaciones_cache) if hasattr(service, '_designaciones_cache') and service._designaciones_cache else 0,
        huayca_materias_count=len(service._huayca_cache) if hasattr(service, '_huayca_cache') and service._huayca_cache else 0,
        faculty_match_rate=faculty_match_rate,
        huayca_match_rate=huayca_match_rate,
        sync_errors=[]
    )

@app.post("/api/refresh-data")
async def refresh_data(
    username: str = Depends(verify_credentials),
    service: CourseTeamService = Depends(get_service)
):
    """Refresh data from all sources (requires authentication)"""
    logger.info(f"User {username} requested data refresh")
    try:
        status = service.refresh_data()
        return {"message": "Data refreshed successfully", "status": status}
    except Exception as e:
        logger.error(f"Data refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Data refresh failed: {str(e)}")

@app.get("/api/courses", response_model=List[Course])
async def get_courses(
    department: Optional[str] = None,
    period: Optional[str] = None,
    career: Optional[str] = None,
    min_team_size: Optional[int] = None,
    service: CourseTeamService = Depends(get_service)
):
    """Get courses with optional filtering"""
    courses = service.detect_unique_courses()
    
    # Apply filters
    if department:
        courses = [c for c in courses if c.department == department]
    
    if period:
        courses = [c for c in courses if c.periodo.value == period]
    
    if career:
        courses = [c for c in courses if c.carrera == career]
    
    if min_team_size:
        courses = [c for c in courses if c.total_team_size >= min_team_size]
    
    return courses

@app.get("/api/courses/{cod_siu}/{periodo}", response_model=Course)
async def get_course_details(
    cod_siu: str, 
    periodo: str,
    service: CourseTeamService = Depends(get_service)
):
    """Get detailed information for a specific course"""
    try:
        period_enum = AcademicPeriod(periodo)
        course = service.get_course_by_code_and_period(cod_siu, period_enum)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        return course
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid period")

@app.get("/api/departments")
async def get_departments(service: CourseTeamService = Depends(get_service)):
    """Get list of available departments"""
    courses = service.detect_unique_courses()
    departments = list(set(c.department for c in courses if c.department))
    return sorted(departments)

@app.get("/api/summary", response_model=CourseTeamSummary)
async def get_summary(service: CourseTeamService = Depends(get_service)):
    """Get comprehensive system summary"""
    return service.generate_summary()

# Web Interface Routes

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request, service: CourseTeamService = Depends(get_service)):
    """Main dashboard page"""
    courses = service.detect_unique_courses()
    summary = service.generate_summary()
    departments = sorted(set(c.department for c in courses if c.department))
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "total_courses": len(courses),
        "total_assignments": summary.total_assignments,
        "unique_faculty": summary.unique_faculty,
        "departments": departments,
        "periods": list(AcademicPeriod),
    })

@app.get("/courses", response_class=HTMLResponse)
async def courses_page(
    request: Request,
    department: Optional[str] = None,
    period: Optional[str] = None,
    career: Optional[str] = None,
    service: CourseTeamService = Depends(get_service)
):
    """Courses listing page with filters"""
    courses = service.detect_unique_courses()
    
    # Apply filters
    if department:
        courses = [c for c in courses if c.department == department]
    if period:
        courses = [c for c in courses if c.periodo.value == period]
    if career:
        courses = [c for c in courses if c.carrera == career]
    
    # Get filter options
    all_courses = service.detect_unique_courses()
    departments = sorted(set(c.department for c in all_courses if c.department))
    careers = sorted(set(c.carrera for c in all_courses))
    
    return templates.TemplateResponse("courses.html", {
        "request": request,
        "courses": courses,
        "departments": departments,
        "careers": careers,
        "periods": list(AcademicPeriod),
        "selected_department": department,
        "selected_period": period,
        "selected_career": career,
    })

@app.get("/course/{cod_siu}/{periodo}", response_class=HTMLResponse)
async def course_detail(
    request: Request,
    cod_siu: str,
    periodo: str,
    service: CourseTeamService = Depends(get_service)
):
    """Course detail page"""
    try:
        period_enum = AcademicPeriod(periodo)
        course = service.get_course_by_code_and_period(cod_siu, period_enum)
        if not course:
            raise HTTPException(status_code=404, detail="Course not found")
        
        return templates.TemplateResponse("course_detail.html", {
            "request": request,
            "course": course,
        })
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid period")

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(
    request: Request, 
    username: str = Depends(verify_credentials),
    service: CourseTeamService = Depends(get_service)
):
    """Admin page for data management"""
    status = await get_data_status(service)
    
    return templates.TemplateResponse("admin.html", {
        "request": request,
        "username": username,
        "status": status,
    })

@app.post("/admin/refresh")
async def admin_refresh(
    username: str = Depends(verify_credentials),
    service: CourseTeamService = Depends(get_service)
):
    """Admin action to refresh data"""
    await refresh_data(username, service)
    return RedirectResponse(url="/admin", status_code=303)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
