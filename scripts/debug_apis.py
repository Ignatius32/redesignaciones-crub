"""
Debug script to investigate API responses.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
from redesignaciones.api.factory import create_google_sheets_client, create_huayca_client
from requests.auth import HTTPDigestAuth

def debug_google_sheets():
    """Debug Google Sheets API response"""
    print("Debugging Google Sheets API...")
    
    try:
        # Create client using factory
        client = create_google_sheets_client()
        print(f"✓ Google Sheets client created successfully")
        
        # First try: getSheets action
        print("\n1. Testing getSheets action...")
        try:
            sheets = client.get_available_sheets()
            print(f"   ✓ Available sheets: {sheets}")
        except Exception as e:
            print(f"   ✗ getSheets failed: {e}")
        
        # Second try: materias_equipo sheet
        print("\n2. Testing materias_equipo sheet...")
        try:
            materias = client.get_materias_equipo()
            print(f"   ✓ Retrieved {len(materias)} materias_equipo records")
            if materias:
                print(f"   ✓ Sample record keys: {list(materias[0].keys())}")
        except Exception as e:
            print(f"   ✗ materias_equipo failed: {e}")
        
        # Third try: designaciones_docentes sheet
        print("\n3. Testing designaciones_docentes sheet...")
        try:
            designaciones = client.get_designaciones_docentes()
            print(f"   ✓ Retrieved {len(designaciones)} designaciones records")
            if designaciones:
                print(f"   ✓ Sample record keys: {list(designaciones[0].keys())}")
        except Exception as e:
            print(f"   ✗ designaciones_docentes failed: {e}")
            
    except Exception as e:
        print(f"✗ Failed to create Google Sheets client: {e}")


def debug_huayca():
    """Debug Huayca API response"""
    print("\nDebugging Huayca API...")
    
    try:
        # Create client using factory
        client = create_huayca_client()
        print(f"✓ Huayca client created successfully")
        
        # Test getting all materias
        print("\n1. Testing get_all_materias...")
        try:
            materias = client.get_all_materias()
            print(f"   ✓ Retrieved {len(materias)} Huayca materias")
            if materias:
                print(f"   ✓ Sample record keys: {list(materias[0].keys())}")
        except Exception as e:
            print(f"   ✗ get_all_materias failed: {e}")
        
        # Test search with filters
        print("\n2. Testing search with filters...")
        try:
            biology_materias = client.search_materias(depto="BIOLOGÍA")
            print(f"   ✓ Found {len(biology_materias)} biology materias")
        except Exception as e:
            print(f"   ✗ search_materias failed: {e}")
            
    except Exception as e:
        print(f"✗ Failed to create Huayca client: {e}")


if __name__ == "__main__":
    print("CRUB APIs Debug Script")
    print("=" * 50)
    debug_google_sheets()
    debug_huayca()
    print("=" * 50)
    print("Debug complete")
