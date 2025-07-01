"""
FastAPI web application for CRUB Course Team Management System.

This application provides REST API endpoints to         <div class="endpoint">
            <span class="method">GET</span> /designaciones/by-desig/{d_desig}
            <br>Get specific designation by D_Desig number
        </div>d manage faculty designations
and course assignments, combining data from Google Sheets and Huayca APIs.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from typing import List, Optional, Dict
import secrets

from .api.factory import create_google_sheets_client, create_huayca_client
from .services.designaciones import DesignacionesService
from .models.types import DocenteDesignacion, DesignacionesSummary, DocenteProfile, DocentesSummary

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="CRUB Course Team Management System",
    description="""
    API for managing faculty designations and course assignments at CRUB.
    
    This system combines data from:
    - Google Sheets API (designaciones_docentes and materias_equipo)
    - Huayca API (detailed course information)
    
    Key relationships:
    - D_Desig (designaciones) ↔ Desig (materias_equipo)
    - Cod_SIU (materias_equipo) ↔ cod_guarani (Huayca)
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Mount static files directory for frontend assets
try:
    from pathlib import Path
    static_dir = Path(__file__).parent / "ui" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
        logger.info(f"Mounted static files from {static_dir}")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Security setup
security = HTTPBasic()

def get_admin_credentials():
    """Get admin credentials from environment variables"""
    return {
        "username": os.getenv("ADMIN_USERNAME", "admin"),
        "password": os.getenv("ADMIN_PASSWORD", "crub2025")
    }

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    """Authenticate admin access"""
    admin_creds = get_admin_credentials()
    is_correct_username = secrets.compare_digest(credentials.username, admin_creds["username"])
    is_correct_password = secrets.compare_digest(credentials.password, admin_creds["password"])
    
    if not (is_correct_username and is_correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Initialize clients and services
try:
    google_client = create_google_sheets_client()
    huayca_client = create_huayca_client()
    designaciones_service = DesignacionesService(google_client, huayca_client)
    logger.info("Successfully initialized all API clients and services")
except Exception as e:
    logger.error(f"Failed to initialize clients: {e}")
    raise

# API Routes

@app.get("/", response_class=HTMLResponse)
async def root():
    """Home page with API information"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CRUB Course Team Management System</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2E86AB; }
            .endpoint { margin: 10px 0; padding: 10px; background: #f5f5f5; border-radius: 5px; }
            .method { font-weight: bold; color: #2E86AB; }
            a { color: #2E86AB; text-decoration: none; }
            a:hover { text-decoration: underline; }
        </style>
    </head>
    <body>
        <h1>CRUB Course Team Management System</h1>
        <p>API for managing faculty designations and course assignments at Centro Regional Universitario Bariloche.</p>
        
        <h2>Available Endpoints</h2>
        
        <div class="endpoint">
            <span class="method">GET</span> <a href="/designaciones">/designaciones</a>
            <br>Get all faculty members with their designations and course assignments
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <a href="/departamentos">/departamentos</a>
            <br>Get designations grouped by department (new frontend view)
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /designaciones/{docente_name}
            <br>Get specific faculty member profile with all designations
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> <a href="/designaciones/flat">/designaciones/flat</a>
            <br>Get all designations as flat list (legacy view)
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /designaciones/by-desig/{d_desig}
            <br>Get specific designation by D_Desig number
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/departamentos
            <br>Get list of all departments with statistics
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /api/departamentos/{departamento}
            <br>Get all designations for a specific department
        </div>
        
        <div class="endpoint">
            <span class="method">POST</span> /admin/cache/clear
            <br>Clear the Huayca data cache (requires authentication)
        </div>
        
        <h2>Documentation</h2>
        <p>
            <a href="/docs">Interactive API Documentation (Swagger UI)</a><br>
            <a href="/redoc">Alternative API Documentation (ReDoc)</a>
        </p>
        
        <h2>Data Sources</h2>
        <ul>
            <li><strong>Google Sheets API:</strong> Faculty designations and course assignments</li>
            <li><strong>Huayca API:</strong> Detailed course information and academic planning</li>
        </ul>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Google Sheets connection
        sheets = google_client.get_available_sheets()
        
        # Test Huayca connection (just a small sample)
        huayca_sample = huayca_client.search_materias(limite=1)  # If supported
        
        return {
            "status": "healthy",
            "services": {
                "google_sheets": "connected",
                "huayca": "connected"
            },
            "available_sheets": sheets
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Service unavailable: {str(e)}"
        )

@app.get("/designaciones", response_model=DocentesSummary)
async def get_all_designaciones():
    """
    Get all faculty members with their designations and course assignments.
    
    This endpoint provides a docente-centric view where each faculty member
    is shown with all their designations grouped together. This properly
    reflects the real data structure where faculty can have multiple appointments.
    
    Key features:
    - Groups multiple designations per faculty member
    - Shows statistics (total designaciones and materias per docente)
    - Includes complete designation and course information
    - Sorted alphabetically by faculty name
    
    Hierarchy: Docente -> Designaciones -> Materias
    """
    try:
        logger.info("API request: get_all_designaciones (docente-centric view)")
        result = designaciones_service.get_docentes_with_designaciones()
        logger.info(f"Returning {result['total_docentes']} docentes with {result['total_designaciones']} designaciones and {result['total_materias_asignadas']} materias")
        return result
    except Exception as e:
        logger.error(f"Error in get_all_designaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch designaciones: {str(e)}"
        )

@app.get("/designaciones/{docente_name}", response_model=Optional[DocenteProfile])
async def get_designacion_by_docente(docente_name: str):
    """
    Get a specific faculty member profile with all their designations.
    
    Args:
        docente_name: Part of the faculty member's name (case-insensitive search)
    
    Returns:
        Complete faculty profile including:
        - Basic information (name, legajo, contact info)
        - Statistics (total designations and courses)
        - All designations with their associated courses
        - Detailed course information from academic system
    
    Example: /designaciones/ANDRADE will find "ANDRADE GAMBOA, JULIO JOSE"
    """
    try:
        logger.info(f"API request: get_designacion_by_docente for {docente_name}")
        result = designaciones_service.get_docente_by_name(docente_name)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Docente with name containing '{docente_name}' not found"
            )
        
        logger.info(f"Returning docente {result['apellido_y_nombre']} with {result['total_designaciones']} designaciones and {result['total_materias']} materias")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_designacion_by_docente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch docente {docente_name}: {str(e)}"
        )

@app.get("/designaciones/flat", response_model=DesignacionesSummary)
async def get_all_designaciones_flat():
    """
    Get all faculty designations as a flat list.
    
    **Note: This is a legacy view. The main /designaciones endpoint provides a better docente-centric view.**
    
    This endpoint returns a flat list of all designations. Since faculty members
    can have multiple designations, the same person may appear multiple times.
    
    For the recommended organized view grouped by faculty member, use GET /designaciones instead.
    """
    try:
        logger.info("API request: get_all_designaciones_flat (legacy flat view)")
        result = designaciones_service.get_designaciones_with_materias()
        logger.info(f"Returning {result['total_designaciones']} designaciones with {result['total_materias_asignadas']} materias (flat view)")
        return result
    except Exception as e:
        logger.error(f"Error in get_all_designaciones_flat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch designaciones: {str(e)}"
        )

@app.get("/designaciones/by-desig/{d_desig}", response_model=Optional[DocenteDesignacion])
async def get_designacion_by_desig(d_desig: str):
    """
    Get a specific faculty designation by D_Desig number.
    
    Args:
        d_desig: The designation number (D_Desig field from designaciones_docentes)
    
    Returns:
        Complete designation information including all related course assignments
        and detailed course information from the academic system.
    """
    try:
        logger.info(f"API request: get_designacion_by_desig for {d_desig}")
        result = designaciones_service.get_designacion_by_desig(d_desig)
        
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Designation {d_desig} not found"
            )
        
        logger.info(f"Returning designation {d_desig} with {len(result['materias'])} materias")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_designacion_by_desig: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch designation {d_desig}: {str(e)}"
        )

# Legacy endpoints for backward compatibility
@app.get("/docentes", response_model=DocentesSummary)
async def get_all_docentes_legacy():
    """Legacy endpoint - use /designaciones instead"""
    return await get_all_designaciones()

@app.get("/docentes/{docente_name}", response_model=Optional[DocenteProfile])
async def get_docente_by_name_legacy(docente_name: str):
    """Legacy endpoint - use /designaciones/{name} instead"""
    return await get_designacion_by_docente(docente_name)

# New department-based endpoints

@app.get("/api/departamentos")
async def get_departamentos_list():
    """
    Get list of all departments with statistics.
    
    Returns a summary of all departments including:
    - Department names
    - Number of designations per department
    - Number of unique faculty members per department
    - Number of course assignments per department
    """
    try:
        logger.info("API request: get_departamentos_list")
        summary = designaciones_service.get_departamentos_summary()
        
        # Transform into a more frontend-friendly format
        result = []
        for dept_name, stats in summary.items():
            result.append({
                "nombre": dept_name,
                "total_designaciones": stats["total_designaciones"],
                "total_docentes": stats["total_docentes"],
                "total_materias": stats["total_materias"]
            })
        
        # Sort by department name
        result.sort(key=lambda d: d["nombre"])
        
        logger.info(f"Returning {len(result)} departments")
        return {
            "total_departamentos": len(result),
            "departamentos": result
        }
    except Exception as e:
        logger.error(f"Error in get_departamentos_list: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch departments: {str(e)}"
        )

@app.get("/api/departamentos/{departamento}")
async def get_designaciones_by_departamento(departamento: str):
    """
    Get all designations for a specific department.
    
    Args:
        departamento: Department name (case-sensitive)
    
    Returns:
        All designations belonging to the specified department,
        ordered by D_Desig, with their associated course assignments.
    """
    try:
        logger.info(f"API request: get_designaciones_by_departamento for {departamento}")
        all_by_dept = designaciones_service.get_designaciones_by_departamento()
        
        if departamento not in all_by_dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Department '{departamento}' not found"
            )
        
        designaciones = all_by_dept[departamento]
        total_materias = sum(len(d['materias']) for d in designaciones)
        unique_docentes = set(d['apellido_y_nombre'] for d in designaciones)
        
        logger.info(f"Returning {len(designaciones)} designaciones for department {departamento}")
        return {
            "departamento": departamento,
            "total_designaciones": len(designaciones),
            "total_docentes": len(unique_docentes),
            "total_materias": total_materias,
            "designaciones": designaciones
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_designaciones_by_departamento: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch designations for department {departamento}: {str(e)}"
        )

@app.get("/departamentos", response_class=HTMLResponse)
async def departamentos_frontend():
    """
    Frontend interface for viewing designations by department.
    
    This endpoint serves the HTML page for the department-based view
    of faculty designations with interactive filtering and sorting.
    """
    try:
        # Read the HTML file
        from pathlib import Path
        html_file = Path(__file__).parent / "ui" / "designaciones.html"
        
        if html_file.exists():
            with open(html_file, 'r', encoding='utf-8') as f:
                return f.read()
        else:
            # Return a basic HTML page if the file doesn't exist yet
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Designaciones por Departamento - CRUB</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h1>Designaciones por Departamento</h1>
                <p>La interfaz frontend está en desarrollo...</p>
                <p><a href="/">← Volver al inicio</a></p>
            </body>
            </html>
            """
    except Exception as e:
        logger.error(f"Error serving departamentos frontend: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to serve frontend: {str(e)}"
        )

# Admin endpoints

@app.post("/admin/cache/clear")
async def clear_cache(username: str = Depends(authenticate)):
    """
    Clear the Huayca data cache.
    
    This endpoint requires authentication and forces a refresh of the cached
    Huayca course data on the next request.
    """
    try:
        logger.info(f"Admin request: clear_cache by {username}")
        designaciones_service.clear_cache()
        logger.info("Cache cleared successfully")
        return {"status": "success", "message": "Huayca data cache cleared"}
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear cache: {str(e)}"
        )

@app.get("/admin/stats")
async def get_stats(username: str = Depends(authenticate)):
    """
    Get system statistics and health information.
    
    This endpoint requires authentication and provides detailed information
    about the current state of the system and data sources.
    """
    try:
        logger.info(f"Admin request: get_stats by {username}")
        
        # Get data from all sources
        designaciones = designaciones_service.get_designaciones_with_materias()
        sheets = google_client.get_available_sheets()
        
        # Calculate some basic statistics
        docentes_with_materias = sum(1 for d in designaciones['designaciones'] if d['materias'])
        avg_materias_per_docente = (designaciones['total_materias_asignadas'] / 
                                  designaciones['total_docentes'] if designaciones['total_docentes'] > 0 else 0)
        
        return {
            "total_designaciones": designaciones['total_designaciones'],
            "total_docentes": designaciones['total_docentes'],
            "total_materias_asignadas": designaciones['total_materias_asignadas'],
            "docentes_with_materias": docentes_with_materias,
            "avg_materias_per_docente": round(avg_materias_per_docente, 2),
            "available_sheets": sheets,
            "cache_status": "active" if designaciones_service._huayca_cache is not None else "empty"
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get stats: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "false").lower() == "true"
    
    logger.info(f"Starting CRUB Course Team Management System on {host}:{port}")
    uvicorn.run(
        "main:app" if not debug else "main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )
