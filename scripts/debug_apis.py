"""
Debug script to investigate API responses.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import requests
from crub_courses.api.factory import GOOGLE_SHEETS_CONFIG, HUAYCA_CONFIG
from requests.auth import HTTPDigestAuth

def debug_google_sheets():
    """Debug Google Sheets API response"""
    print("Debugging Google Sheets API...")
    
    url = GOOGLE_SHEETS_CONFIG["base_url"]
    
    # First try: getSheets action
    print("\n1. Testing getSheets action...")
    params = {
        "secret": GOOGLE_SHEETS_CONFIG["secret"],
        "action": "getSheets"
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text (first 500 chars): {response.text[:500]}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"JSON Response: {json_data}")
            except Exception as e:
                print(f"JSON Parse Error: {e}")
        else:
            print("Response is not JSON")
            
    except Exception as e:
        print(f"Request Error: {e}")
    
    # Second try: materias_equipo sheet
    print("\n2. Testing materias_equipo sheet...")
    params = {
        "secret": GOOGLE_SHEETS_CONFIG["secret"],
        "sheet": "materias_equipo"
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text (first 500 chars): {response.text[:500]}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"JSON Response Type: {type(json_data)}")
                if isinstance(json_data, list):
                    print(f"JSON List Length: {len(json_data)}")
                elif isinstance(json_data, dict):
                    print(f"JSON Dict Keys: {list(json_data.keys())}")
            except Exception as e:
                print(f"JSON Parse Error: {e}")
        else:
            print("Response is not JSON")
            
    except Exception as e:
        print(f"Request Error: {e}")
    
    # Third try: basic auth test (no sheet specified)
    print("\n3. Testing basic auth (no sheet)...")
    params = {
        "secret": GOOGLE_SHEETS_CONFIG["secret"]
    }
    
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=15)
        print(f"Status Code: {response.status_code}")
        print(f"Content-Type: {response.headers.get('content-type')}")
        print(f"Response Text (first 200 chars): {response.text[:200]}")
            
    except Exception as e:
        print(f"Request Error: {e}")

def debug_huayca():
    """Debug Huayca API response"""
    print("\nDebugging Huayca API...")
    
    url = HUAYCA_CONFIG["base_url"]
    auth = HTTPDigestAuth(HUAYCA_CONFIG["username"], HUAYCA_CONFIG["password"])
    
    print(f"URL: {url}")
    print(f"Auth: {HUAYCA_CONFIG['username']}:***")
    
    try:
        response = requests.get(
            url, 
            auth=auth, 
            timeout=10,
            verify=False,
            headers={"Accept": "application/json"}
        )
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        print(f"Response Text (first 500 chars): {response.text[:500]}")
        
        if response.headers.get('content-type', '').startswith('application/json'):
            try:
                json_data = response.json()
                print(f"JSON Response Type: {type(json_data)}")
                if isinstance(json_data, list):
                    print(f"JSON List Length: {len(json_data)}")
                    if json_data:
                        print(f"First Item Keys: {list(json_data[0].keys())}")
                elif isinstance(json_data, dict):
                    print(f"JSON Dict Keys: {list(json_data.keys())}")
            except Exception as e:
                print(f"JSON Parse Error: {e}")
        else:
            print("Response is not JSON")
            
    except Exception as e:
        print(f"Request Error: {e}")

if __name__ == "__main__":
    debug_google_sheets()
    debug_huayca()
