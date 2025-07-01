"""
Factory functions for creating API clients.

This module provides factory functions to create configured instances of API clients.
"""

import os
from pathlib import Path
from .clients import GoogleSheetsClient, HuaycaClient


def _load_env_file():
    """Load environment variables from .env file if it exists"""
    env_file = Path(__file__).parent.parent.parent.parent / ".env"
    if env_file.exists():
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


# Load environment variables
_load_env_file()


def create_google_sheets_client() -> GoogleSheetsClient:
    """Create a configured Google Sheets client"""
    base_url = os.getenv("GOOGLE_SHEETS_BASE_URL")
    secret = os.getenv("GOOGLE_SHEETS_SECRET")
    
    if not base_url:
        raise ValueError("GOOGLE_SHEETS_BASE_URL environment variable is required")
    if not secret:
        raise ValueError("GOOGLE_SHEETS_SECRET environment variable is required")
    
    return GoogleSheetsClient(
        base_url=base_url,
        secret=secret
    )


def create_huayca_client() -> HuaycaClient:
    """Create a configured Huayca client"""
    base_url = os.getenv("HUAYCA_BASE_URL")
    username = os.getenv("HUAYCA_USERNAME")
    password = os.getenv("HUAYCA_PASSWORD")
    
    if not base_url:
        raise ValueError("HUAYCA_BASE_URL environment variable is required")
    if not username:
        raise ValueError("HUAYCA_USERNAME environment variable is required")
    if not password:
        raise ValueError("HUAYCA_PASSWORD environment variable is required")
    
    return HuaycaClient(
        base_url=base_url,
        username=username,
        password=password
    )
