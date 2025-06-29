"""
Script to run the FastAPI application for CRUB Course Team Management.

This script initializes and runs the FastAPI application with proper configuration.
"""

import sys
import os
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

if __name__ == "__main__":
    import uvicorn
    
    print("Starting CRUB Course Team Management FastAPI Server...")
    print("Dashboard: http://localhost:8000")
    print("API Documentation: http://localhost:8000/api/docs")
    print("Admin Panel: http://localhost:8000/admin (credentials from .env file)")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Use the app import string for proper reload functionality
    uvicorn.run(
        "src.crub_courses.ui.fastapi_app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_dirs=[str(project_root / "src")]
    )
