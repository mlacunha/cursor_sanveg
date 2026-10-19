from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal

# Nested location schemas
from app.schemas.estado import EstadoResponse
from app.schemas.municipio import MunicipioResponse

# Schema inline para Produtor (proprietário)
class ProdutorInlinePropriedade(BaseModel):
    id: str
    nome: str
    cpf_cnpj: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None

    model_config = {"from_attributes": True}


# Schema para criação de propriedade
class PropriedadeCreate(BaseModel):
    n_cadastro: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    RG_IE: Optional[str] = None
    nome: str = Field(..., min_length=1, max_length=100)
    CEP: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    UF: Optional[str] = None
    area_total: Optional[float] = None
    destino_producao: Optional[str] = None
    id_proprietario: Optional[str] = None
    classificacao: Optional[str] = None
    producao_familiar: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


# Schema para atualização parcial (PATCH)
class PropriedadeUpdate(BaseModel):
    n_cadastro: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    RG_IE: Optional[str] = None
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    CEP: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    UF: Optional[str] = None
    area_total: Optional[float] = None
    destino_producao: Optional[str] = None
    id_proprietario: Optional[str] = None
    classificacao: Optional[str] = None
    producao_familiar: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None


# Schema de resposta
class PropriedadeResponse(BaseModel):
    id: str
    n_cadastro: Optional[str] = None
    cpf_cnpj: Optional[str] = None
    RG_IE: Optional[str] = None
    nome: str
    CEP: Optional[str] = None
    endereco: Optional[str] = None
    bairro: Optional[str] = None
    municipio: Optional[str] = None
    UF: Optional[str] = None
    area_total: Optional[float] = None
    destino_producao: Optional[str] = None
    id_proprietario: Optional[str] = None
    classificacao: Optional[str] = None
    producao_familiar: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    coordenada: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime

    # Nested location objects
    uf_info: Optional["EstadoResponse"] = None
    municipio_info: Optional["MunicipioResponse"] = None
    
    # Dados do proprietário (produtor) - opcional
    proprietario_data: Optional[ProdutorInlinePropriedade] = None

    model_config = {"from_attributes": True}
