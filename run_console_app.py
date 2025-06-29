#!/usr/bin/env python3
"""
Entry point for the CRUB Course Team Console Application.

This script provides a command-line interface for viewing and filtering
course teams by department and other criteria.

Usage: python run_console_app.py
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crub_courses.ui.console_app import CourseConsoleViewer

if __name__ == "__main__":
    app = CourseConsoleViewer()
    app.run()
