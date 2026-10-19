from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class OrgaoTipoInline(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str


class OrgaoBase(BaseModel):
    sigla: Optional[str] = Field(None, max_length=20)
    nome: str = Field(..., min_length=1, max_length=100)
    id_tipo_orgao: Optional[str] = Field(None, max_length=36)
    cnpj: Optional[str] = Field(None, max_length=20)
    logo: Optional[str] = Field("", max_length=255)
    url_logo: Optional[str] = Field("", max_length=255)
    servidor_logo: Optional[str] = Field("", max_length=255)
    UF_sede: Optional[str] = Field("", max_length=10)


class OrgaoCreate(OrgaoBase):
    id: Optional[str] = Field(None, max_length=36)


class OrgaoUpdate(BaseModel):
    sigla: Optional[str] = Field(None, max_length=20)
    nome: Optional[str] = Field(None, min_length=1, max_length=100)
    id_tipo_orgao: Optional[str] = Field(None, max_length=36)
    cnpj: Optional[str] = Field(None, max_length=20)
    logo: Optional[str] = Field(None, max_length=255)
    url_logo: Optional[str] = Field(None, max_length=255)
    servidor_logo: Optional[str] = Field(None, max_length=255)
    UF_sede: Optional[str] = Field(None, max_length=10)


class OrgaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    sigla: Optional[str] = None
    nome: str
    id_tipo_orgao: Optional[str] = None
    cnpj: Optional[str] = None
    logo: Optional[str] = None
    url_logo: Optional[str] = None
    servidor_logo: Optional[str] = None
    UF_sede: Optional[str] = None
    criado_em: datetime
    atualizado_em: datetime
    orgao_tipo_data: Optional[OrgaoTipoInline] = None
