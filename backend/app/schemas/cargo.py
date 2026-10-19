from pydantic import BaseModel, ConfigDict
from typing import Optional


class OrgaoInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sigla: Optional[str] = None
    nome: str


class CargoCreate(BaseModel):
    id: Optional[str] = None
    id_orgao: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    descricao: Optional[str] = None


class CargoUpdate(BaseModel):
    id_orgao: Optional[str] = None
    sigla: Optional[str] = None
    nome: Optional[str] = None
    descricao: Optional[str] = None


class CargoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_orgao: Optional[str] = None
    sigla: Optional[str] = None
    nome: str
    descricao: Optional[str] = None
    orgao_data: Optional[OrgaoInline] = None
