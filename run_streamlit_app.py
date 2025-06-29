#!/usr/bin/env python3
"""
Entry point for the CRUB Course Team Streamlit Web Application.

This script starts the Streamlit web application for viewing and filtering
course teams through a modern web interface.

Usage: python run_streamlit_app.py
"""

import sys
import os
import subprocess

if __name__ == "__main__":
    # Add the src directory to the Python path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    env = os.environ.copy()
    env['PYTHONPATH'] = src_path + os.pathsep + env.get('PYTHONPATH', '')
    
    # Get the path to the Streamlit app
    app_path = os.path.join(os.path.dirname(__file__), 'src', 'crub_courses', 'ui', 'streamlit_app.py')
    
    # Start Streamlit
    subprocess.run([
        sys.executable, "-m", "streamlit", "run", app_path
    ], env=env)
