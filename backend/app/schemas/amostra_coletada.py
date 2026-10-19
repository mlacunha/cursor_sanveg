from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime, date
from decimal import Decimal


class AmostraColetadaCreate(BaseModel):
    id: Optional[str] = None
    id_area_programa: str = Field(..., description="UUID do registro area_programa")
    envelope: Optional[str] = Field(None, max_length=30)
    parte_coletada: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_envio_laboratorio: Optional[date] = None
    id_laboratorio: Optional[str] = None
    processo_sei: Optional[str] = None
    data_resultado: Optional[date] = None
    resultado_laboratorio: Optional[str] = None
    laudo_arquivo: Optional[str] = None


class AmostraColetadaUpdate(BaseModel):
    envelope: Optional[str] = Field(None, max_length=30)
    parte_coletada: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_envio_laboratorio: Optional[date] = None
    id_laboratorio: Optional[str] = None
    processo_sei: Optional[str] = None
    data_resultado: Optional[date] = None
    resultado_laboratorio: Optional[str] = None
    laudo_arquivo: Optional[str] = None


class AmostraColetadaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    id_area_programa: str
    envelope: Optional[str] = None
    parte_coletada: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_envio_laboratorio: Optional[date] = None
    id_laboratorio: Optional[str] = None
    processo_sei: Optional[str] = None
    data_resultado: Optional[date] = None
    resultado_laboratorio: Optional[str] = None
    laudo_arquivo: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
