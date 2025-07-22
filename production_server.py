#!/usr/bin/env python3
"""
Production startup script for CRUB Course Team Management System (redesignaciones)

This script is designed to run the FastAPI application in production mode
using uvicorn server, suitable for deployment behind Apache with ProxyPass.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup the Python environment for production"""
    # Add the src directory to the Python path
    project_root = Path(__file__).parent
    src_dir = project_root / "src"
    
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Load environment variables from .env file if it exists
    env_file = project_root / ".env"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    
    # Set production defaults
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("HOST", "127.0.0.1")
    os.environ.setdefault("PORT", "8001")  # Different port to avoid conflicts

def main():
    """Main startup function for production"""
    print("Starting CRUB Course Team Management System (Production)")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Import and run the FastAPI app with uvicorn
    try:
        import uvicorn
        
        # Get configuration from environment
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8001"))
        
        print(f"Starting production server on http://{host}:{port}")
        print(f"Application module: redesignaciones.main:app")
        print("=" * 60)
        
        # Run with production settings
        uvicorn.run(
            "redesignaciones.main:app",
            host=host,
            port=port,
            reload=False,  # No reload in production
            log_level="info",
            access_log=True,
            workers=1  # Single worker for now, can be increased
        )
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
