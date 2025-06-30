"""
Service layer for processing and combining data from multiple APIs.

This module provides services to fetch and combine data from Google Sheets and Huayca APIs,
creating enriched data structures for the FastAPI webapp.
"""

import logging
from typing import List, Dict, Optional
from collections import defaultdict

from ..api.clients import GoogleSheetsClient, HuaycaClient
from ..models.types import (
    DocenteDesignacion, MateriaAsignada, HuaycaMateriaDetalle,
    DesignacionesSummary, MateriasEquipoRawRecord, DesignacionesDocentesRawRecord,
    HuaycaMateriasRawRecord
)

logger = logging.getLogger(__name__)


class DesignacionesService:
    """Service for processing faculty designations and related course data"""
    
    def __init__(self, google_client: GoogleSheetsClient, huayca_client: HuaycaClient):
        self.google_client = google_client
        self.huayca_client = huayca_client
        
        # Cache for Huayca data to avoid repeated API calls
        self._huayca_cache: Optional[List[HuaycaMateriasRawRecord]] = None
    
    def _get_huayca_data(self) -> List[HuaycaMateriasRawRecord]:
        """Get all Huayca materias with caching"""
        if self._huayca_cache is None:
            logger.info("Fetching Huayca materias data")
            self._huayca_cache = self.huayca_client.get_all_materias()
            logger.info(f"Cached {len(self._huayca_cache)} Huayca materias")
        return self._huayca_cache
    
    def _create_huayca_lookup(self) -> Dict[str, HuaycaMateriasRawRecord]:
        """Create a lookup dictionary for Huayca data by cod_guarani"""
        huayca_data = self._get_huayca_data()
        lookup = {}
        
        for materia in huayca_data:
            cod_guarani = materia.get('cod_guarani', '').strip()
            if cod_guarani:
                lookup[cod_guarani] = materia
        
        logger.info(f"Created Huayca lookup with {len(lookup)} entries")
        return lookup
    
    def _convert_designacion_record(self, record: DesignacionesDocentesRawRecord) -> DocenteDesignacion:
        """Convert a raw designacion record to the processed format"""
        return DocenteDesignacion(
            id_redesignacion=record.get('id_redesignacion', 0),
            d_desig=record.get('D Desig', ''),  # Note: space in field name
            uni_acad=record.get('Uni Acad', ''), # Note: space in field name
            año=record.get('Año', ''),
            norma=record.get('Norma', ''),
            cuerpo=record.get('Cuerpo', ''),
            legajo=record.get('Legajo', ''),
            documento=record.get('Documento', ''),
            cuil=record.get('CUIL', ''),
            fecha_ingreso=record.get('Fecha Ingreso', ''), # Note: space in field name
            apellido_y_nombre=record.get('Apellido y Nombre', ''), # Note: spaces in field name
            sexo=record.get('Sexo', ''),
            fecha_nacim=record.get('Fecha Nacim', ''), # Note: space in field name
            correos=record.get('Correos', ''),
            cat_mapuche=record.get('Cat Mapuche', ''), # Note: space in field name
            cat_estatuto=record.get('Cat Estatuto', ''), # Note: space in field name
            dedicacion=record.get('Dedicación', ''),
            caracter=record.get('Carácter', ''),
            desde=record.get('Desde', ''),
            hasta=record.get('Hasta', ''),
            departamento=record.get('Departamento', ''),
            area=record.get('Área', ''),
            orientacion=record.get('Orientación', ''),
            lsgh=record.get('LSGH?', ''), # Note: question mark in field name
            estado=record.get('Estado', ''),
            materias=[]
        )
    
    def _convert_materia_record(
        self, 
        record: MateriasEquipoRawRecord, 
        huayca_lookup: Dict[str, HuaycaMateriasRawRecord]
    ) -> MateriaAsignada:
        """Convert a raw materia_equipo record to the processed format with Huayca details"""
        cod_siu = record.get('Cod SIU', '').strip()  # Note: space in field name
        
        # Look up detailed information from Huayca
        huayca_detail = None
        if cod_siu and cod_siu in huayca_lookup:
            huayca_record = huayca_lookup[cod_siu]
            huayca_detail = HuaycaMateriaDetalle(
                id_materia=huayca_record.get('id_materia', 0),
                nombre_carrera=huayca_record.get('nombre_carrera', ''),
                nombre_materia=huayca_record.get('nombre_materia', ''),
                ano_plan=huayca_record.get('ano_plan', 0),
                periodo_plan=huayca_record.get('periodo_plan', ''),
                horas_totales=huayca_record.get('horas_totales', ''),
                horas_semanales=huayca_record.get('horas_semanales', ''),
                depto_principal=huayca_record.get('depto_principal', ''),
                depto=huayca_record.get('depto', ''),
                area=huayca_record.get('area', ''),
                orientacion=huayca_record.get('orientacion', ''),
                contenidos_minimos=huayca_record.get('contenidos_minimos', ''),
                correlativas_para_cursar=huayca_record.get('correlativas_para_cursar', ''),
                correlativas_para_aprobar=huayca_record.get('correlativas_para_aprobar', ''),
                competencias=huayca_record.get('competencias', ''),
                optativa=huayca_record.get('optativa', ''),
                trayecto=huayca_record.get('trayecto', ''),
                cod_carrera=huayca_record.get('cod_carrera', ''),
                plan_guarani=huayca_record.get('plan_guarani', ''),
                version_guarani=huayca_record.get('version_guarani', ''),
                plan_mocovi=huayca_record.get('plan_mocovi', ''),
                plan_ordenanzas=huayca_record.get('plan_ordenanzas', ''),
                cod_guarani=huayca_record.get('cod_guarani', ''),
                observaciones=huayca_record.get('observaciones', '')
            )
        
        return MateriaAsignada(
            id_redesignacion_materia=record.get('id_redesignacion', 0),
            materia_nombre=record.get('Materia', ''),
            cod_siu=cod_siu,
            carrera=record.get('Carrera', ''),
            ordenanza=record.get('Ordenanza', ''),
            docente=record.get('Docente', ''),
            categoria=record.get('Categoría', ''),
            desde=record.get('Desde', ''),
            hasta=record.get('Hasta', ''),
            lic=record.get('Lic', ''),
            modulo=record.get('Módulo', ''),
            rol=record.get('Rol', ''),
            periodo=record.get('Período', ''),
            estado_materia=record.get('Estado', ''),
            materia_detalle=huayca_detail
        )
    
    def get_designaciones_with_materias(self) -> DesignacionesSummary:
        """
        Get all designaciones with their related materias.
        
        This method:
        1. Fetches designaciones_docentes data
        2. Fetches materias_equipo data
        3. Fetches Huayca materias data for detailed course information
        4. Links designaciones with materias using D_Desig <-> Desig relationship
        5. Enriches materia data with Huayca details using Cod_SIU <-> cod_guarani relationship
        """
        logger.info("Starting to fetch and process all designation data")
        
        # Fetch all data
        logger.info("Fetching designaciones_docentes data")
        designaciones_raw = self.google_client.get_designaciones_docentes()
        
        logger.info("Fetching materias_equipo data")
        materias_raw = self.google_client.get_materias_equipo()
        
        # Create Huayca lookup
        huayca_lookup = self._create_huayca_lookup()
        
        # Create materias lookup by Desig (maps to D_Desig in designaciones)
        materias_by_desig = defaultdict(list)
        for materia_record in materias_raw:
            desig = materia_record.get('Desig', '').strip()
            if desig:
                converted_materia = self._convert_materia_record(materia_record, huayca_lookup)
                materias_by_desig[desig].append(converted_materia)
        
        logger.info(f"Created materias lookup with {len(materias_by_desig)} designations")
        
        # Process designaciones and link with materias
        designaciones = []
        total_materias = 0
        
        for designacion_record in designaciones_raw:
            designacion = self._convert_designacion_record(designacion_record)
            d_desig = designacion['d_desig'].strip()
            
            # Find related materias for this designation
            if d_desig in materias_by_desig:
                designacion['materias'] = materias_by_desig[d_desig]
                total_materias += len(designacion['materias'])
                logger.debug(f"Found {len(designacion['materias'])} materias for designation {d_desig}")
            
            designaciones.append(designacion)
        
        logger.info(f"Processed {len(designaciones)} designaciones with {total_materias} total materias")
        
        return DesignacionesSummary(
            total_designaciones=len(designaciones),
            total_docentes=len(designaciones),
            total_materias_asignadas=total_materias,
            designaciones=designaciones
        )
    
    def get_designacion_by_desig(self, d_desig: str) -> Optional[DocenteDesignacion]:
        """Get a specific designation by D_Desig with its related materias"""
        logger.info(f"Fetching designation for D_Desig: {d_desig}")
        
        # For now, get all and filter - could be optimized with API filters if available
        all_designaciones = self.get_designaciones_with_materias()
        
        for designacion in all_designaciones['designaciones']:
            if designacion['d_desig'] == d_desig:
                logger.info(f"Found designation {d_desig} with {len(designacion['materias'])} materias")
                return designacion
        
        logger.warning(f"Designation {d_desig} not found")
        return None
    
    def get_designaciones_by_docente(self, docente_name: str) -> List[DocenteDesignacion]:
        """Get all designations for a specific faculty member (by name)"""
        logger.info(f"Fetching designations for docente: {docente_name}")
        
        all_designaciones = self.get_designaciones_with_materias()
        result = []
        
        for designacion in all_designaciones['designaciones']:
            if docente_name.lower() in designacion['apellido_y_nombre'].lower():
                result.append(designacion)
        
        logger.info(f"Found {len(result)} designations for docente {docente_name}")
        return result
    
    def clear_cache(self):
        """Clear the Huayca data cache"""
        self._huayca_cache = None
        logger.info("Cleared Huayca data cache")
