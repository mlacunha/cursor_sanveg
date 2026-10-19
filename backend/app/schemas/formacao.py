from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class FormacaoCreate(BaseModel):
    id: Optional[str] = None
    nome: str


class FormacaoUpdate(BaseModel):
    nome: Optional[str] = None


class FormacaoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    nome: str
    criado_em: datetime
    atualizado_em: datetime
