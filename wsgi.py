"""
WSGI Configuration for CRUB Course Team Management System (redesignaciones)

This file provides WSGI compatibility for deploying the FastAPI application
on Apache with mod_wsgi.
"""

import os
import sys
from pathlib import Path

# Add the project directories to Python path
project_root = Path(__file__).parent
src_dir = project_root / "src"

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))

# Load environment variables from .env file if it exists
env_file = project_root / ".env"
if env_file.exists():
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip())

# Set default environment variables for production
os.environ.setdefault("DEBUG", "false")
os.environ.setdefault("HOST", "0.0.0.0")
os.environ.setdefault("PORT", "8000")

# Import and create the FastAPI application
try:
    from redesignaciones.main import app
    
    # For WSGI compatibility, we need to wrap the FastAPI app
    # Install asgiref if not already installed
    try:
        from asgiref.wsgi import WsgiToAsgi
        application = WsgiToAsgi(app)
    except ImportError:
        # Alternative approach using uvicorn's WSGI handler
        import uvicorn
        from uvicorn.middleware.wsgi import WSGIMiddleware
        
        # Create a simple WSGI application that starts FastAPI
        def application(environ, start_response):
            # This is a workaround - FastAPI is ASGI, not WSGI
            # For proper deployment, consider using uvicorn with a process manager
            try:
                import asyncio
                from uvicorn.main import Server, Config
                
                # Create uvicorn config
                config = Config(
                    app="redesignaciones.main:app",
                    host="127.0.0.1",
                    port=8000,
                    log_level="info"
                )
                
                # This approach won't work well with mod_wsgi
                # We need a different solution
                status = '500 Internal Server Error'
                headers = [('Content-type', 'text/plain')]
                start_response(status, headers)
                return [b'FastAPI requires ASGI server. Please use uvicorn or configure Apache with mod_proxy.']
                
            except Exception as e:
                status = '500 Internal Server Error'
                headers = [('Content-type', 'text/plain')]
                start_response(status, headers)
                return [f'Error: {str(e)}'.encode()]

except ImportError as e:
    def application(environ, start_response):
        status = '500 Internal Server Error'
        headers = [('Content-type', 'text/plain')]
        start_response(status, headers)
        return [f'Import error: {str(e)}'.encode()]

# Note: FastAPI is an ASGI application, not WSGI
# For Apache deployment, it's better to use ProxyPass to uvicorn
# or use an ASGI-to-WSGI adapter like asgiref
