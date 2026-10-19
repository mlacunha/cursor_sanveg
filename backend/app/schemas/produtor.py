from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime

# Avoid circular import by using forward refs; import models used for nested fields
from app.schemas.estado import EstadoResponse
from app.schemas.municipio import MunicipioResponse


class ProdutorCreate(BaseModel):
    """Schema for creating a new Produtor"""
    n_cadastro: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    RG_IE: Optional[str] = None
    nome: str
    CEP: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class ProdutorUpdate(BaseModel):
    """Schema for updating a Produtor (partial update with PATCH)"""
    n_cadastro: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    RG_IE: Optional[str] = None
    nome: Optional[str] = None
    CEP: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[EmailStr] = None


class ProdutorResponse(BaseModel):
    """Schema for Produtor response"""
    model_config = ConfigDict(from_attributes=True)
    
    id: str
    n_cadastro: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    RG_IE: Optional[str] = None
    nome: str
    CEP: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None
    telefone: Optional[str] = None
    email: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    # Nested location objects for convenience
    uf_info: Optional["EstadoResponse"] = None
    municipio_info: Optional["MunicipioResponse"] = None