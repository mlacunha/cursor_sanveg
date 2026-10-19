from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProgramaCreate(BaseModel):
    """Schema for creating a new Programa"""
    codigo: Optional[str] = None
    nome: str
    nomes_comuns: Optional[str] = None
    nome_cientifico: Optional[str] = None


class ProgramaUpdate(BaseModel):
    """Schema for updating a Programa (partial update with PATCH)"""
    codigo: Optional[str] = None
    nome: Optional[str] = None
    nomes_comuns: Optional[str] = None
    nome_cientifico: Optional[str] = None


class ProgramaResponse(BaseModel):
    """Schema for Programa response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    codigo: Optional[str] = None
    nome: str
    nomes_comuns: Optional[str] = None
    nome_cientifico: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
