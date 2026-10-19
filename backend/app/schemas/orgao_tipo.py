from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class OrgaoTipoBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)


class OrgaoTipoCreate(OrgaoTipoBase):
    id: Optional[str] = Field(None, max_length=36)


class OrgaoTipoUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    descricao: Optional[str] = Field(None, max_length=255)


class OrgaoTipoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    descricao: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
