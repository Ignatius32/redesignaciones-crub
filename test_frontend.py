#!/usr/bin/env python3
"""
Quick test script to verify the frontend data flow.
"""

import requests
import json

def test_departamentos_api():
    """Test the departamentos API endpoints"""
    print("Testing departamentos API endpoints...")
    
    try:
        # Test main departamentos list
        print("\n1. Testing /api/departamentos")
        response = requests.get("http://127.0.0.1:8000/api/departamentos")
        response.raise_for_status()
        data = response.json()
        
        print(f"   ✓ Found {data['total_departamentos']} departments")
        
        # Find a department with materias
        dept_with_materias = None
        for dept in data['departamentos']:
            if dept['total_materias'] > 0:
                dept_with_materias = dept
                break
        
        if dept_with_materias:
            dept_name = dept_with_materias['nombre']
            print(f"   ✓ Testing department: {dept_name} ({dept_with_materias['total_materias']} materias)")
            
            # Test specific department
            print(f"\n2. Testing /api/departamentos/{dept_name}")
            response = requests.get(f"http://127.0.0.1:8000/api/departamentos/{dept_name}")
            response.raise_for_status()
            dept_data = response.json()
            
            print(f"   ✓ Retrieved {len(dept_data['designaciones'])} designaciones")
            
            # Find a designation with materias
            designacion_with_materias = None
            for des in dept_data['designaciones']:
                if des.get('materias') and len(des['materias']) > 0:
                    designacion_with_materias = des
                    break
            
            if designacion_with_materias:
                print(f"   ✓ Found designation {designacion_with_materias['d_desig']} with {len(designacion_with_materias['materias'])} materias")
                
                # Check first materia structure
                first_materia = designacion_with_materias['materias'][0]
                print(f"   ✓ First materia: {first_materia.get('materia_nombre', 'NO NAME')}")
                print(f"   ✓ Has materia_detalle: {'Yes' if first_materia.get('materia_detalle') else 'No'}")
                
                if first_materia.get('materia_detalle'):
                    detalle = first_materia['materia_detalle']
                    print(f"   ✓ Huayca details: {detalle.get('horas_totales', 'N/A')} hs totales")
                
                return True
            else:
                print("   ✗ No designations with materias found in this department")
        else:
            print("   ✗ No departments with materias found")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return False

def test_specific_designation():
    """Test a specific designation endpoint"""
    print("\n3. Testing specific designation...")
    
    try:
        # Get a designation with materias from the flat endpoint
        response = requests.get("http://127.0.0.1:8000/designaciones/flat")
        response.raise_for_status()
        data = response.json()
        
        # Find designation with materias
        designation_with_materias = None
        for des in data['designaciones']:
            if des.get('materias') and len(des['materias']) > 0:
                designation_with_materias = des
                break
        
        if designation_with_materias:
            d_desig = designation_with_materias['d_desig']
            print(f"   ✓ Testing designation {d_desig}")
            
            response = requests.get(f"http://127.0.0.1:8000/designaciones/by-desig/{d_desig}")
            response.raise_for_status()
            des_data = response.json()
            
            print(f"   ✓ Designation: {des_data['apellido_y_nombre']}")
            print(f"   ✓ Department: {des_data['departamento']}")
            print(f"   ✓ Materias: {len(des_data.get('materias', []))}")
            
            if des_data.get('materias'):
                first_materia = des_data['materias'][0]
                print(f"   ✓ First materia: {first_materia.get('materia_nombre')}")
                print(f"   ✓ Codigo: {first_materia.get('cod_siu')}")
                print(f"   ✓ Has details: {'Yes' if first_materia.get('materia_detalle') else 'No'}")
                
            return True
        else:
            print("   ✗ No designations with materias found")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    return False

if __name__ == "__main__":
    print("Frontend Data Flow Test")
    print("=" * 50)
    
    success1 = test_departamentos_api()
    success2 = test_specific_designation()
    
    print("\n" + "=" * 50)
    if success1 and success2:
        print("✅ All tests passed! Frontend should display materias correctly.")
    else:
        print("❌ Some tests failed. Check the API responses.")
        
    print("\nTo test the frontend:")
    print("1. Open http://127.0.0.1:8000/departamentos")
    print("2. Click on a department to expand it")
    print("3. Click on a designation row to see materias")
    print("4. Look for materias with detailed Huayca information")
