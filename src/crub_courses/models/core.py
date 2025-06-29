"""
Core data models for CRUB Course Team Management System.

This module defines the main data structures for courses, faculty members, and their relationships
based on the three data sources: Google Sheets (materias_equipo, designaciones_docentes)
and Huayca API (course details).
"""

from typing import List, Optional
from pydantic import BaseModel, Field, validator
from enum import Enum


class AcademicPeriod(str, Enum):
    """Academic periods from the materias_equipo data"""
    FIRST_QUADRIMESTER = "1CUAT"
    SECOND_QUADRIMESTER = "2CUAT"
    ANNUAL = "ANUAL"
    SECOND_BIMESTER_2C = "2BIMES2C"
    MONTHLY = "MENSU"


class FacultyRole(str, Enum):
    """Faculty roles in course assignments"""
    RESPONSIBLE = "Resp"
    AUXILIARY = "Aux"


class OptativeStatus(str, Enum):
    """Whether a course is elective or required"""
    YES = "SI"
    NO = "NO"


class FacultyDetails(BaseModel):
    """Faculty personal details from designaciones_docentes sheet"""
    
    id_redesignacion: int
    d_desig: str = Field(alias="D Desig")
    uni_acad: str = Field(alias="Uni Acad")
    año: str = Field(alias="Año")
    norma: str = Field(alias="Norma")
    cuerpo: str = Field(alias="Cuerpo")
    legajo: str = Field(alias="Legajo")
    documento: str = Field(alias="Documento")
    cuil: str = Field(alias="CUIL")
    fecha_ingreso: str = Field(alias="Fecha Ingreso")
    apellido_nombre: str = Field(alias="Apellido y Nombre")
    sexo: str = Field(alias="Sexo")
    fecha_nacim: str = Field(alias="Fecha Nacim")
    correos: str = Field(alias="Correos")
    cat_mapuche: str = Field(alias="Cat Mapuche")
    cat_estatuto: str = Field(alias="Cat Estatuto")
    dedicacion: str = Field(alias="Dedicación")
    caracter: str = Field(alias="Carácter")
    desde: str = Field(alias="Desde")
    hasta: str = Field(alias="Hasta")
    departamento: str = Field(alias="Departamento")
    area: str = Field(alias="Área")
    orientacion: str = Field(alias="Orientación")
    lsgh: str = Field(alias="LSGH?")

    class Config:
        validate_by_name = True
        populate_by_name = True


class TeamMember(BaseModel):
    """A faculty member assigned to a course from materias_equipo"""
    
    id_redesignacion: int
    materia: str = Field(alias="Materia")
    cod_siu: str = Field(alias="Cod SIU")
    carrera: str = Field(alias="Carrera")
    ordenanza: str = Field(alias="Ordenanza")
    docente: str = Field(alias="Docente")
    legajo: str = Field(alias="Legajo")
    categoria: str = Field(alias="Categoría")
    desig: str = Field(alias="Desig")
    desde: str = Field(alias="Desde")
    hasta: str = Field(alias="Hasta")
    lic: str = Field(alias="Lic")
    modulo: str = Field(alias="Módulo")
    rol: FacultyRole = Field(alias="Rol")
    periodo: AcademicPeriod = Field(alias="Período")
    estado: str = Field(alias="Estado")
    
    # Enriched data from designaciones_docentes
    personal_details: Optional[FacultyDetails] = None

    class Config:
        validate_by_name = True
        populate_by_name = True


class HuaycaCourseDetails(BaseModel):
    """Course academic details from Huayca API"""
    
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
    optativa: OptativeStatus
    trayecto: str
    cod_carrera: str
    plan_guarani: str
    version_guarani: str
    plan_mocovi: str
    plan_ordenanzas: str
    cod_guarani: str
    observaciones: str

    @validator('optativa', pre=True)
    def validate_optativa(cls, v):
        if isinstance(v, str):
            return OptativeStatus.YES if v.upper() == "SI" else OptativeStatus.NO
        return v


class Course(BaseModel):
    """
    A unique course identified by Cod SIU + Período combination.
    Contains team members and enriched details from Huayca.
    """
    
    # Core identification
    cod_siu: str
    materia: str
    periodo: AcademicPeriod
    carrera: str
    
    # Team members from materias_equipo
    team_members: List[TeamMember] = []
    
    # Enriched academic details from Huayca
    huayca_details: Optional[HuaycaCourseDetails] = None
    
    @property
    def unique_key(self) -> str:
        """Unique identifier for this course"""
        return f"{self.cod_siu}_{self.periodo}"
    
    @property
    def responsible_faculty(self) -> List[TeamMember]:
        """Get faculty members with responsible role"""
        return [member for member in self.team_members if member.rol == FacultyRole.RESPONSIBLE]
    
    @property
    def auxiliary_faculty(self) -> List[TeamMember]:
        """Get faculty members with auxiliary role"""
        return [member for member in self.team_members if member.rol == FacultyRole.AUXILIARY]
    
    @property
    def total_team_size(self) -> int:
        """Total number of team members"""
        return len(self.team_members)
    
    @property
    def department(self) -> Optional[str]:
        """Get department from Huayca details if available"""
        return self.huayca_details.depto if self.huayca_details else None
    
    @property
    def academic_area(self) -> Optional[str]:
        """Get academic area from Huayca details if available"""
        return self.huayca_details.area if self.huayca_details else None
    
    @property
    def is_elective(self) -> Optional[bool]:
        """Check if course is elective"""
        if self.huayca_details:
            return self.huayca_details.optativa == OptativeStatus.YES
        return None
