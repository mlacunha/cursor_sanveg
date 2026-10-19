from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProgramaInline(BaseModel):
    """Nested schema for Programa relationship in Norma"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    codigo: Optional[str] = None
    nome: str


class NormaCreate(BaseModel):
    """Schema for creating a new Norma"""
    id_programa: str
    nome_norma: str
    ementa: str
    url_publicacao: Optional[str] = None


class NormaUpdate(BaseModel):
    """Schema for updating a Norma (partial update with PATCH)"""
    id_programa: Optional[str] = None
    nome_norma: Optional[str] = None
    ementa: Optional[str] = None
    url_publicacao: Optional[str] = None


class NormaResponse(BaseModel):
    """Schema for Norma response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    id_programa: str
    nome_norma: str
    ementa: str
    url_publicacao: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    
    # Optional nested programa data
    programa: Optional[ProgramaInline] = None
