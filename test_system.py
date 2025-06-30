"""
Test script for the CRUB Course Team Management System.

This script tests the basic functionality of the designaciones service
and demonstrates how to use the API clients.
"""

import sys
import os
import logging
from pathlib import Path

# Add the src directory to the Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from crub_courses.api.factory import create_google_sheets_client, create_huayca_client
from crub_courses.services.designaciones import DesignacionesService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_api_connections():
    """Test basic API connections"""
    print("=" * 60)
    print("Testing API Connections")
    print("=" * 60)
    
    try:
        # Test Google Sheets client
        print("1. Testing Google Sheets connection...")
        google_client = create_google_sheets_client()
        sheets = google_client.get_available_sheets()
        print(f"   ✓ Connected to Google Sheets. Available sheets: {sheets}")
        
        # Test Huayca client
        print("2. Testing Huayca connection...")
        huayca_client = create_huayca_client()
        materias_sample = huayca_client.search_materias()[:5]  # Get first 5
        print(f"   ✓ Connected to Huayca. Sample materias count: {len(materias_sample)}")
        
        return google_client, huayca_client
        
    except Exception as e:
        print(f"   ✗ Connection test failed: {e}")
        return None, None


def test_data_fetching(google_client, huayca_client):
    """Test data fetching from both APIs"""
    print("\n" + "=" * 60)
    print("Testing Data Fetching")
    print("=" * 60)
    
    try:
        # Test Google Sheets data
        print("1. Fetching designaciones_docentes...")
        designaciones = google_client.get_designaciones_docentes()
        print(f"   ✓ Fetched {len(designaciones)} designaciones records")
        
        print("2. Fetching materias_equipo...")
        materias_equipo = google_client.get_materias_equipo()
        print(f"   ✓ Fetched {len(materias_equipo)} materias_equipo records")
        
        print("3. Fetching Huayca materias...")
        huayca_materias = huayca_client.get_all_materias()
        print(f"   ✓ Fetched {len(huayca_materias)} Huayca materias")
        
        return designaciones, materias_equipo, huayca_materias
        
    except Exception as e:
        print(f"   ✗ Data fetching failed: {e}")
        return None, None, None


def test_designaciones_service(google_client, huayca_client):
    """Test the designaciones service integration"""
    print("\n" + "=" * 60)
    print("Testing Designaciones Service")
    print("=" * 60)
    
    try:
        # Initialize service
        print("1. Initializing DesignacionesService...")
        service = DesignacionesService(google_client, huayca_client)
        print("   ✓ Service initialized successfully")
        
        # Test getting all designaciones with materias
        print("2. Fetching all designaciones with materias...")
        all_designaciones = service.get_designaciones_with_materias()
        
        print(f"   ✓ Total designaciones: {all_designaciones['total_designaciones']}")
        print(f"   ✓ Total docentes: {all_designaciones['total_docentes']}")
        print(f"   ✓ Total materias asignadas: {all_designaciones['total_materias_asignadas']}")
        
        # Show some examples
        print("3. Analyzing data relationships...")
        designaciones_with_materias = [d for d in all_designaciones['designaciones'] if d['materias']]
        print(f"   ✓ Designaciones with materias: {len(designaciones_with_materias)}")
        
        if designaciones_with_materias:
            example = designaciones_with_materias[0]
            print(f"   ✓ Example: {example['apellido_y_nombre']} (D_Desig: {example['d_desig']})")
            print(f"     - Has {len(example['materias'])} materias")
            
            if example['materias']:
                materia_example = example['materias'][0]
                print(f"     - First materia: {materia_example['materia_nombre']}")
                print(f"     - Cod_SIU: {materia_example['cod_siu']}")
                print(f"     - Has Huayca detail: {'Yes' if materia_example['materia_detalle'] else 'No'}")
        
        # Test specific designation lookup
        if designaciones_with_materias:
            d_desig = designaciones_with_materias[0]['d_desig']
            print(f"4. Testing specific designation lookup for {d_desig}...")
            specific = service.get_designacion_by_desig(d_desig)
            if specific:
                print(f"   ✓ Found designation: {specific['apellido_y_nombre']}")
            else:
                print(f"   ✗ Designation {d_desig} not found")
        
        return True
        
    except Exception as e:
        print(f"   ✗ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def analyze_data_relationships(designaciones, materias_equipo, huayca_materias):
    """Analyze the relationships between different data sources"""
    print("\n" + "=" * 60)
    print("Analyzing Data Relationships")
    print("=" * 60)
    
    try:
        # Analyze D_Desig <-> Desig relationship
        d_desigs = set()
        for d in designaciones:
            d_desig = d.get('D Desig', '').strip()  # Note: space in field name
            if d_desig:
                d_desigs.add(d_desig)
        
        desigs = set()
        for m in materias_equipo:
            desig = m.get('Desig', '').strip()
            if desig:
                desigs.add(desig)
        
        print(f"1. D_Desig <-> Desig relationship:")
        print(f"   - Unique D_Desig values: {len(d_desigs)}")
        print(f"   - Unique Desig values: {len(desigs)}")
        print(f"   - Matching values: {len(d_desigs & desigs)}")
        print(f"   - D_Desigs without Desig: {len(d_desigs - desigs)}")
        print(f"   - Desigs without D_Desig: {len(desigs - d_desigs)}")
        
        # Analyze Cod_SIU <-> cod_guarani relationship
        cod_sius = set()
        for m in materias_equipo:
            cod_siu = m.get('Cod SIU', '').strip()  # Note: space in field name
            if cod_siu:
                cod_sius.add(cod_siu)
        
        cod_guaranis = set()
        for h in huayca_materias:
            cod_guarani = h.get('cod_guarani', '').strip()
            if cod_guarani:
                cod_guaranis.add(cod_guarani)
        
        print(f"2. Cod_SIU <-> cod_guarani relationship:")
        print(f"   - Unique Cod_SIU values: {len(cod_sius)}")
        print(f"   - Unique cod_guarani values: {len(cod_guaranis)}")
        print(f"   - Matching values: {len(cod_sius & cod_guaranis)}")
        print(f"   - Cod_SIUs without cod_guarani: {len(cod_sius - cod_guaranis)}")
        print(f"   - cod_guaranis without Cod_SIU: {len(cod_guaranis - cod_sius)}")
        
        # Show some examples
        if d_desigs & desigs:
            common_desig = list(d_desigs & desigs)[0]
            print(f"3. Example matching designation: {common_desig}")
        
        if cod_sius & cod_guaranis:
            common_cod = list(cod_sius & cod_guaranis)[0]
            print(f"4. Example matching course code: {common_cod}")
        
    except Exception as e:
        print(f"   ✗ Analysis failed: {e}")


def main():
    """Main test function"""
    print("CRUB Course Team Management System - Test Script")
    print("=" * 60)
    
    # Test API connections
    google_client, huayca_client = test_api_connections()
    if not google_client or not huayca_client:
        print("❌ API connections failed. Please check your .env configuration.")
        return
    
    # Test data fetching
    designaciones, materias_equipo, huayca_materias = test_data_fetching(google_client, huayca_client)
    if not designaciones or not materias_equipo or not huayca_materias:
        print("❌ Data fetching failed.")
        return
    
    # Analyze data relationships
    analyze_data_relationships(designaciones, materias_equipo, huayca_materias)
    
    # Test the integrated service
    service_success = test_designaciones_service(google_client, huayca_client)
    
    print("\n" + "=" * 60)
    if service_success:
        print("✅ All tests passed! The system is ready to use.")
        print("\nTo start the FastAPI server, run:")
        print("   python -m uvicorn src.crub_courses.main:app --reload")
        print("\nThen visit http://localhost:8000 for the web interface.")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
    print("=" * 60)


if __name__ == "__main__":
    main()
