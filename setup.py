"""
Setup configuration for CRUB Course Team Management System.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="crub-courses",
    version="1.0.0",
    author="CRUB Development Team",
    author_email="dev@crub.uncoma.edu.ar",
    description="A system for detecting course teams and aggregating data from multiple sources",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/crub/redesignaciones-crub",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pydantic>=1.10.0,<3.0.0",
        "requests>=2.25.0",
        "streamlit>=1.20.0",
        "plotly>=5.0.0",
        "pandas>=1.3.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-mock>=3.0",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.900",
        ],
        "test": [
            "pytest>=6.0",
            "pytest-mock>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "crub-console=crub_courses.ui.console_app:main",
            "crub-streamlit=crub_courses.ui.streamlit_app:main",
        ],
    },
)
