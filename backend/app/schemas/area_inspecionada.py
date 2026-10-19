from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class AreaInspecionadaCreate(BaseModel):
    id: Optional[str] = None
    id_termo_inspecao: str
    tipo_area: Optional[str] = None
    nome_local: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    obs: Optional[str] = None


class AreaInspecionadaUpdate(BaseModel):
    tipo_area: Optional[str] = None
    nome_local: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    obs: Optional[str] = None


class AreaInspecionadaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    id_termo_inspecao: str
    tipo_area: Optional[str] = None
    nome_local: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    obs: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime
