"""
Startup script for the CRUB Course Team Management System FastAPI application.

This script configures the Python environment and starts the FastAPI server.
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup the Python environment"""
    # Add the src directory to the Python path
    src_dir = Path(__file__).parent / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))
    
    # Load environment variables
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print(f"Loading environment from {env_file}")
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())
    else:
        print("Warning: .env file not found. Make sure environment variables are set.")

def main():
    """Main startup function"""
    print("=" * 60)
    print("CRUB Course Team Management System")
    print("=" * 60)
    
    # Setup environment
    setup_environment()
    
    # Import and run the FastAPI app
    try:
        import uvicorn
        
        # Get configuration from environment
        host = os.getenv("HOST", "127.0.0.1")
        port = int(os.getenv("PORT", "8000"))
        debug = os.getenv("DEBUG", "false").lower() == "true"
        
        print(f"Starting server on http://{host}:{port}")
        print("Available endpoints:")
        print(f"  - Home page: http://{host}:{port}/")
        print(f"  - API docs: http://{host}:{port}/docs")
        print(f"  - Health check: http://{host}:{port}/health")
        print(f"  - All designaciones: http://{host}:{port}/designaciones")
        print("")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        
        uvicorn.run(
            "redesignaciones.main:app",  # Use string import for reload to work
            host=host,
            port=port,
            reload=debug,
            log_level="info"
        )
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed:")
        print("  pip install -r requirements.txt")
    except Exception as e:
        print(f"Error starting server: {e}")

if __name__ == "__main__":
    main()
