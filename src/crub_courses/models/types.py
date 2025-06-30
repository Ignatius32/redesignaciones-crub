"""
Type definitions for CRUB Course Management data structures.

This module contains TypedDict definitions for raw API responses and processed data models.
"""

from typing import List, Optional, Any, Dict

try:
    from typing_extensions import TypedDict
except ImportError:
    from typing import TypedDict


# Raw API response types
class MateriasEquipoRawRecord(TypedDict, total=False):
    """Raw record from materias_equipo Google Sheets API"""
    id_redesignacion: int
    Materia: str
    # Note: Using 'Cod SIU' with space as shown in API docs
    Cod_SIU: str  # Maps to cod_guarani in Huayca API  
    Carrera: str
    Ordenanza: str
    Docente: str
    Legajo: str
    Categoría: str
    Desig: str  # Maps to D_Desig in designaciones_docentes
    Desde: str
    Hasta: str
    Lic: str
    Módulo: str
    Rol: str
    Período: str
    Estado: str


class DesignacionesDocentesRawRecord(TypedDict, total=False):
    """Raw record from designaciones_docentes Google Sheets API"""
    id_redesignacion: int
    # Note: Using 'D Desig' with space as shown in API docs
    D_Desig: str  # Maps to Desig in materias_equipo
    Uni_Acad: str
    Año: str
    Norma: str
    Cuerpo: str
    Legajo: str
    Documento: str
    CUIL: str
    # Note: Using 'Fecha Ingreso' with space as shown in API docs
    Fecha_Ingreso: str
    # Note: Using 'Apellido y Nombre' with spaces as shown in API docs  
    Apellido_y_Nombre: str
    Sexo: str
    # Note: Using 'Fecha Nacim' with space as shown in API docs
    Fecha_Nacim: str
    Correos: str
    # Note: Using 'Cat Mapuche' with space as shown in API docs
    Cat_Mapuche: str
    # Note: Using 'Cat Estatuto' with space as shown in API docs
    Cat_Estatuto: str
    Dedicación: str
    Carácter: str
    Desde: str
    Hasta: str
    Departamento: str
    Área: str
    Orientación: str
    # Note: Using 'LSGH?' as shown in API docs
    LSGH: str
    Estado: str


class HuaycaMateriasRawRecord(TypedDict, total=False):
    """Raw record from Huayca materias API"""
    id_materia: int
    nombre_carrera: str
    nombre_materia: str
    ano_plan: int
    periodo_plan: str
    horas_totales: str
    horas_semanales: str
    depto_principal: str
    depto: str
    area: str
    orientacion: str
    contenidos_minimos: str
    correlativas_para_cursar: str
    correlativas_para_aprobar: str
    competencias: str
    optativa: str
    trayecto: str
    cod_carrera: str
    plan_guarani: str
    version_guarani: str
    plan_mocovi: str
    plan_ordenanzas: str
    cod_guarani: str  # Maps to Cod_SIU in materias_equipo
    observaciones: str


# API response types
MateriasEquipoRaw = List[MateriasEquipoRawRecord]
DesignacionesDocentesRaw = List[DesignacionesDocentesRawRecord]
HuaycaMateriasRaw = List[HuaycaMateriasRawRecord]


# Processed data models
class DocenteDesignacion(TypedDict):
    """A faculty member's designation with related course information"""
    # Designation data
    id_redesignacion: int
    d_desig: str
    uni_acad: str
    año: str
    norma: str
    cuerpo: str
    legajo: str
    documento: str
    cuil: str
    fecha_ingreso: str
    apellido_y_nombre: str
    sexo: str
    fecha_nacim: str
    correos: str
    cat_mapuche: str
    cat_estatuto: str
    dedicacion: str
    caracter: str
    desde: str
    hasta: str
    departamento: str
    area: str
    orientacion: str
    lsgh: str
    estado: str
    
    # Related materias (courses) for this designation
    materias: List['MateriaAsignada']


class MateriaAsignada(TypedDict):
    """A course assignment linked to a designation"""
    # From materias_equipo
    id_redesignacion_materia: int
    materia_nombre: str
    cod_siu: str
    carrera: str
    ordenanza: str
    docente: str
    categoria: str
    desde: str
    hasta: str
    lic: str
    modulo: str
    rol: str
    periodo: str
    estado_materia: str
    
    # From Huayca API (when cod_siu matches cod_guarani)
    materia_detalle: Optional['HuaycaMateriaDetalle']


class HuaycaMateriaDetalle(TypedDict):
    """Detailed course information from Huayca API"""
    id_materia: int
    nombre_carrera: str
    nombre_materia: str
    ano_plan: int
    periodo_plan: str
    horas_totales: str
    horas_semanales: str
    depto_principal: str
    depto: str
    area: str
    orientacion: str
    contenidos_minimos: str
    correlativas_para_cursar: str
    correlativas_para_aprobar: str
    competencias: str
    optativa: str
    trayecto: str
    cod_carrera: str
    plan_guarani: str
    version_guarani: str
    plan_mocovi: str
    plan_ordenanzas: str
    cod_guarani: str
    observaciones: str


class DesignacionesSummary(TypedDict):
    """Summary of designaciones with statistics"""
    total_designaciones: int
    total_docentes: int
    total_materias_asignadas: int
    designaciones: List[DocenteDesignacion]
