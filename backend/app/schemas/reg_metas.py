from pydantic import BaseModel, ConfigDict
from typing import Optional


class ProgramaInlineRegMetas(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str


class RegMetasCreate(BaseModel):
    programa: str
    descricao: int
    ano: int
    trimestre: int
    und: str


class RegMetasUpdate(BaseModel):
    programa: Optional[str] = None
    descricao: Optional[int] = None
    ano: Optional[int] = None
    trimestre: Optional[int] = None
    und: Optional[str] = None


class RegMetasResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    programa: str
    descricao: int
    ano: int
    trimestre: int
    und: str
    programa_data: Optional[ProgramaInlineRegMetas] = None
