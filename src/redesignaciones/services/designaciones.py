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
    DesignacionesSummary, DocenteProfile, DocentesSummary, 
    MateriasEquipoRawRecord, DesignacionesDocentesRawRecord,
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
    
    def get_docentes_with_designaciones(self) -> DocentesSummary:
        """
        Get all docentes with their designations and materias.
        
        This method properly handles the hierarchy:
        Docente -> Multiple Designaciones -> Multiple Materias per Designación
        
        Returns a docente-centric view where each faculty member has
        all their designations grouped together.
        """
        logger.info("Starting to fetch and process all docentes with designaciones")
        
        # Get all designaciones first
        all_designaciones = self.get_designaciones_with_materias()
        
        # Group designaciones by docente (apellido_y_nombre)
        docentes_map = defaultdict(list)
        for designacion in all_designaciones['designaciones']:
            docente_name = designacion['apellido_y_nombre'].strip()
            if docente_name:
                docentes_map[docente_name].append(designacion)
        
        # Create docente profiles
        docentes = []
        total_materias = 0
        
        for docente_name, designaciones_list in docentes_map.items():
            # Use the most complete/recent designation for basic info
            primary_designation = max(designaciones_list, key=lambda d: len(d.get('correos', '')))
            
            # Count total materias for this docente
            docente_materias = sum(len(d['materias']) for d in designaciones_list)
            total_materias += docente_materias
            
            docente_profile = DocenteProfile(
                apellido_y_nombre=primary_designation['apellido_y_nombre'],
                legajo=primary_designation['legajo'],
                documento=primary_designation['documento'],
                cuil=primary_designation['cuil'],
                sexo=primary_designation['sexo'],
                fecha_nacim=primary_designation['fecha_nacim'],
                correos=primary_designation['correos'],
                total_designaciones=len(designaciones_list),
                total_materias=docente_materias,
                designaciones=designaciones_list
            )
            
            docentes.append(docente_profile)
        
        # Sort docentes by name
        docentes.sort(key=lambda d: d['apellido_y_nombre'])
        
        logger.info(f"Processed {len(docentes)} docentes with {all_designaciones['total_designaciones']} designaciones and {total_materias} materias")
        
        return DocentesSummary(
            total_docentes=len(docentes),
            total_designaciones=all_designaciones['total_designaciones'],
            total_materias_asignadas=total_materias,
            docentes=docentes
        )
    
    def get_docente_by_name(self, docente_name: str) -> Optional[DocenteProfile]:
        """Get a specific docente profile with all their designations"""
        logger.info(f"Fetching docente profile for: {docente_name}")
        
        all_docentes = self.get_docentes_with_designaciones()
        
        for docente in all_docentes['docentes']:
            if docente_name.lower() in docente['apellido_y_nombre'].lower():
                logger.info(f"Found docente {docente['apellido_y_nombre']} with {docente['total_designaciones']} designaciones and {docente['total_materias']} materias")
                return docente
        
        logger.warning(f"Docente {docente_name} not found")
        return None
    
    def get_docentes_by_partial_name(self, partial_name: str) -> List[DocenteProfile]:
        """Get all docentes matching a partial name"""
        logger.info(f"Searching docentes with partial name: {partial_name}")
        
        all_docentes = self.get_docentes_with_designaciones()
        result = []
        
        for docente in all_docentes['docentes']:
            if partial_name.lower() in docente['apellido_y_nombre'].lower():
                result.append(docente)
        
        logger.info(f"Found {len(result)} docentes matching '{partial_name}'")
        return result

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
    
    def get_designaciones_by_departamento(self) -> Dict[str, List[DocenteDesignacion]]:
        """
        Get all designaciones grouped by departamento.
        
        Returns a dictionary where keys are department names and values are
        lists of designaciones belonging to that department, ordered by D_Desig.
        """
        logger.info("Fetching designaciones grouped by departamento")
        
        all_designaciones = self.get_designaciones_with_materias()
        
        # Group by departamento
        by_department = defaultdict(list)
        for designacion in all_designaciones['designaciones']:
            dept = designacion.get('departamento', '').strip()
            if not dept:
                dept = 'SIN DEPARTAMENTO'
            by_department[dept].append(designacion)
        
        # Sort designaciones within each department by D_Desig
        for dept in by_department:
            by_department[dept].sort(key=lambda d: d.get('d_desig', ''))
        
        # Convert to regular dict and sort department names
        result = dict(sorted(by_department.items()))
        
        logger.info(f"Grouped designaciones into {len(result)} departments")
        for dept, designaciones in result.items():
            logger.info(f"  {dept}: {len(designaciones)} designaciones")
        
        return result
    
    def get_departamentos_summary(self) -> Dict[str, Dict[str, int]]:
        """
        Get summary statistics for each department.
        
        Returns a dictionary with department names as keys and statistics as values:
        - total_designaciones: number of designations
        - total_docentes: number of unique faculty members
        - total_materias: number of course assignments
        """
        logger.info("Calculating department summary statistics")
        
        designaciones_by_dept = self.get_designaciones_by_departamento()
        summary = {}
        
        for dept, designaciones in designaciones_by_dept.items():
            # Count unique docentes
            unique_docentes = set()
            total_materias = 0
            
            for designacion in designaciones:
                unique_docentes.add(designacion['apellido_y_nombre'])
                total_materias += len(designacion['materias'])
            
            summary[dept] = {
                'total_designaciones': len(designaciones),
                'total_docentes': len(unique_docentes),
                'total_materias': total_materias
            }
        
        logger.info(f"Calculated statistics for {len(summary)} departments")
        return summary

    def clear_cache(self):
        """Clear the Huayca data cache"""
        self._huayca_cache = None
        logger.info("Cleared Huayca data cache")
