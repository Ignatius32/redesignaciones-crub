"""
Data models and type definitions for CRUB Course Management.

This module contains TypedDict definitions for raw API responses 
and processed data models used throughout the application.
"""

from .types import (
    # Raw API types
    MateriasEquipoRaw,
    DesignacionesDocentesRaw, 
    HuaycaMateriasRaw,
    MateriasEquipoRawRecord,
    DesignacionesDocentesRawRecord,
    HuaycaMateriasRawRecord,
    
    # Processed data models
    DocenteDesignacion,
    MateriaAsignada,
    HuaycaMateriaDetalle,
    DesignacionesSummary
)

__all__ = [
    # Raw API types
    "MateriasEquipoRaw",
    "DesignacionesDocentesRaw", 
    "HuaycaMateriasRaw",
    "MateriasEquipoRawRecord",
    "DesignacionesDocentesRawRecord",
    "HuaycaMateriasRawRecord",
    
    # Processed data models
    "DocenteDesignacion",
    "MateriaAsignada", 
    "HuaycaMateriaDetalle",
    "DesignacionesSummary"
]
