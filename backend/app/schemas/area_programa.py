from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProgramaInlineAreaPrograma(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str


class AreaProgramaCreate(BaseModel):
    id: Optional[str] = None
    id_area: str
    id_programa: str
    especie: Optional[str] = None
    variedade: Optional[str] = None
    material_multiplicacao: Optional[str] = None
    origem: Optional[str] = None
    idade_plantio: Optional[Decimal] = None
    area_plantada: Optional[Decimal] = None
    numero_plantas: Optional[int] = None
    numero_inspecionadas: Optional[int] = None
    numero_suspeitas: Optional[int] = None
    resultado: Optional[str] = None
    obs: Optional[str] = None


class AreaProgramaUpdate(BaseModel):
    id_programa: Optional[str] = None
    especie: Optional[str] = None
    variedade: Optional[str] = None
    material_multiplicacao: Optional[str] = None
    origem: Optional[str] = None
    idade_plantio: Optional[Decimal] = None
    area_plantada: Optional[Decimal] = None
    numero_plantas: Optional[int] = None
    numero_inspecionadas: Optional[int] = None
    numero_suspeitas: Optional[int] = None
    resultado: Optional[str] = None
    obs: Optional[str] = None


class AreaProgramaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    id_area: str
    id_programa: str
    especie: Optional[str] = None
    variedade: Optional[str] = None
    material_multiplicacao: Optional[str] = None
    origem: Optional[str] = None
    idade_plantio: Optional[Decimal] = None
    area_plantada: Optional[Decimal] = None
    numero_plantas: Optional[int] = None
    numero_inspecionadas: Optional[int] = None
    numero_suspeitas: Optional[int] = None
    resultado: Optional[str] = None
    obs: Optional[str] = None
    data_criacao: datetime
    data_atualizacao: datetime
    programa_data: Optional[ProgramaInlineAreaPrograma] = None
