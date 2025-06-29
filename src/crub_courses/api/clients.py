"""
API clients for external data sources.

This module contains the client implementations for Google Sheets and Huayca APIs.
"""

import requests
from requests.auth import HTTPDigestAuth
from typing import List, Dict, Any, Optional
import logging
from urllib.parse import urlencode

from ..models.types import MateriasEquipoRaw, DesignacionesDocentesRaw, HuaycaMateriasRaw

logger = logging.getLogger(__name__)


class GoogleSheetsAPIError(Exception):
    """Exception raised for Google Sheets API errors"""
    pass


class HuaycaAPIError(Exception):
    """Exception raised for Huayca API errors"""
    pass


class GoogleSheetsClient:
    """Client for Google Sheets API with CRUD operations"""
    
    def __init__(self, base_url: str, secret: str):
        self.base_url = base_url
        self.secret = secret
        self.session = requests.Session()
    
    def _make_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Make a request to the Google Sheets API"""
        # Add secret to parameters
        params["secret"] = self.secret
        
        try:
            logger.info(f"Making Google Sheets API request with params: {params}")
            response = self.session.get(self.base_url, params=params)
            response.raise_for_status()
            
            # Check if response is JSON
            content_type = response.headers.get('content-type', '')
            if 'application/json' not in content_type:
                raise GoogleSheetsAPIError(f"Expected JSON response, got {content_type}")
            
            data = response.json()
            
            # Handle API error responses
            if isinstance(data, dict) and data.get("status") == "error":
                raise GoogleSheetsAPIError(f"API Error: {data.get('message', 'Unknown error')}")
            
            return data
            
        except requests.RequestException as e:
            raise GoogleSheetsAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise GoogleSheetsAPIError(f"Invalid JSON response: {str(e)}")
    
    def get_available_sheets(self) -> List[str]:
        """Get list of available sheets"""
        params = {"action": "getSheets"}
        response = self._make_request(params)
        
        if isinstance(response, dict) and "sheets" in response:
            return response["sheets"]
        else:
            raise GoogleSheetsAPIError("Unexpected response format for getSheets")
    
    def get_materias_equipo(self) -> MateriasEquipoRaw:
        """Get materias_equipo data"""
        logger.info("Fetching materias_equipo data from Google Sheets")
        
        params = {"sheet": "materias_equipo"}
        data = self._make_request(params)
        
        if not isinstance(data, list):
            raise GoogleSheetsAPIError(f"Expected list response, got {type(data)}")
        
        logger.info(f"Retrieved {len(data)} materias_equipo records")
        return data
    
    def get_designaciones_docentes(self) -> DesignacionesDocentesRaw:
        """Get designaciones_docentes data"""
        logger.info("Fetching designaciones_docentes data from Google Sheets")
        
        params = {"sheet": "designaciones_docentes"}
        data = self._make_request(params)
        
        if not isinstance(data, list):
            raise GoogleSheetsAPIError(f"Expected list response, got {type(data)}")
        
        logger.info(f"Retrieved {len(data)} designaciones_docentes records")
        return data


class HuaycaClient:
    """Client for Huayca API with search and filter capabilities"""
    
    def __init__(self, base_url: str, username: str, password: str):
        self.base_url = base_url
        self.auth = HTTPDigestAuth(username, password)
        self.session = requests.Session()
        # Disable SSL verification for Huayca's self-signed certificate
        self.session.verify = False
    
    def _make_request(self, params: Optional[Dict[str, Any]] = None) -> HuaycaMateriasRaw:
        """Make a request to the Huayca API"""
        try:
            logger.debug(f"Making Huayca API request with params: {params}")
            response = self.session.get(
                self.base_url,
                params=params,
                auth=self.auth
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not isinstance(data, list):
                raise HuaycaAPIError(f"Expected list response, got {type(data)}")
            
            return data
            
        except requests.RequestException as e:
            raise HuaycaAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise HuaycaAPIError(f"Invalid JSON response: {str(e)}")
    
    def get_all_materias(self) -> HuaycaMateriasRaw:
        """Get all materias from Huayca"""
        logger.info("Fetching all materias from Huayca API")
        data = self._make_request()
        logger.info(f"Retrieved {len(data)} materias from Huayca")
        return data
    
    def search_materias(self, **filters) -> HuaycaMateriasRaw:
        """Search materias with filters"""
        logger.info(f"Searching Huayca materias with filters: {filters}")
        data = self._make_request(params=filters)
        logger.info(f"Found {len(data)} materias matching filters")
        return data
    
    def get_materias_by_career(self, career_code: str) -> HuaycaMateriasRaw:
        """Get all courses for a specific career"""
        return self.search_materias(cod_carrera=career_code)
    
    def get_elective_materias(self) -> HuaycaMateriasRaw:
        """Get all elective courses"""
        return self.search_materias(optativa="SI")
