from pydantic import BaseModel, ConfigDict
from typing import Optional


class OrgaoInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sigla: Optional[str] = None
    nome: str


class UnidadeCreate(BaseModel):
    id: Optional[str] = None
    id_orgao: Optional[str] = None
    nome: str
    municipio: Optional[str] = None
    uf: Optional[str] = None


class UnidadeUpdate(BaseModel):
    id_orgao: Optional[str] = None
    nome: Optional[str] = None
    municipio: Optional[str] = None
    uf: Optional[str] = None


class UnidadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_orgao: Optional[str] = None
    nome: str
    municipio: Optional[str] = None
    uf: Optional[str] = None
    orgao_data: Optional[OrgaoInline] = None
