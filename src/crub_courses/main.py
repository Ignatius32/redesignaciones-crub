"""
FastAPI web application for CRUB Course Team Management System.

This application provides REST API endpoints to access and manage faculty designations
and course assignments, combining data from Google Sheets and Huayca APIs.
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
import logging
from typing import List, Optional
import secrets

from .api.factory import create_google_sheets_client, create_huayca_client
from .services.designaciones import DesignacionesService
from .models.types import DocenteDesignacion, DesignacionesSummary

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
            <br>Get all faculty designations with related course assignments
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /designaciones/{d_desig}
            <br>Get specific designation by D_Desig number
        </div>
        
        <div class="endpoint">
            <span class="method">GET</span> /designaciones/docente/{docente_name}
            <br>Get all designations for a specific faculty member
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

@app.get("/designaciones", response_model=DesignacionesSummary)
async def get_all_designaciones():
    """
    Get all faculty designations with their related course assignments.
    
    This endpoint combines:
    - Faculty designation data from Google Sheets
    - Course assignment data from Google Sheets  
    - Detailed course information from Huayca API
    
    Returns a comprehensive list linking each designation (D_Desig) with:
    - All related course assignments (matching Desig)
    - Detailed course information from academic system (matching Cod_SIU to cod_guarani)
    """
    try:
        logger.info("API request: get_all_designaciones")
        result = designaciones_service.get_designaciones_with_materias()
        logger.info(f"Returning {result['total_designaciones']} designaciones with {result['total_materias_asignadas']} materias")
        return result
    except Exception as e:
        logger.error(f"Error in get_all_designaciones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch designaciones: {str(e)}"
        )

@app.get("/designaciones/{d_desig}", response_model=Optional[DocenteDesignacion])
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

@app.get("/designaciones/docente/{docente_name}", response_model=List[DocenteDesignacion])
async def get_designaciones_by_docente(docente_name: str):
    """
    Get all designations for a specific faculty member.
    
    Args:
        docente_name: Part of the faculty member's name (case-insensitive search)
    
    Returns:
        List of all designations for the specified faculty member, each with
        their related course assignments and detailed course information.
    """
    try:
        logger.info(f"API request: get_designaciones_by_docente for {docente_name}")
        result = designaciones_service.get_designaciones_by_docente(docente_name)
        logger.info(f"Returning {len(result)} designaciones for docente {docente_name}")
        return result
    except Exception as e:
        logger.error(f"Error in get_designaciones_by_docente: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch designaciones for {docente_name}: {str(e)}"
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
