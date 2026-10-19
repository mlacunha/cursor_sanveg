from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ProgramaInlineRegAtividade(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str


class RegAtividadeCreate(BaseModel):
    user: str
    data: datetime
    processo_sei: str
    programa: str
    descricao: str


class RegAtividadeUpdate(BaseModel):
    user: Optional[str] = None
    data: Optional[datetime] = None
    processo_sei: Optional[str] = None
    programa: Optional[str] = None
    descricao: Optional[str] = None


class RegAtividadeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user: str
    data: datetime
    processo_sei: str
    programa: str
    descricao: str
    programa_data: Optional[ProgramaInlineRegAtividade] = None
