from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProgramaInline(BaseModel):
    """Nested schema for Programa relationship in Hospedeiro"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    codigo: Optional[str] = None
    nome: str


class HospedeiroCreate(BaseModel):
    """Schema for creating a new Hospedeiro"""
    id_programa: str
    nomes_comuns: str
    nome_cientifico: str


class HospedeiroUpdate(BaseModel):
    """Schema for updating a Hospedeiro (partial update with PATCH)"""
    id_programa: Optional[str] = None
    nomes_comuns: Optional[str] = None
    nome_cientifico: Optional[str] = None


class HospedeiroResponse(BaseModel):
    """Schema for Hospedeiro response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    id_programa: str
    nomes_comuns: str
    nome_cientifico: str
    criado_em: datetime
    atualizado_em: datetime
    
    # Optional nested programa data
    programa: Optional[ProgramaInline] = None
