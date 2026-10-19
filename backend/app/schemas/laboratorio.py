from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class LaboratorioBase(BaseModel):
    nome: str = Field(..., description="Nome ou razao social do laboratorio")
    tipo: Optional[str] = Field(default=None, description="LFDA ou Credenciado")
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    contato: Optional[str] = None
    instrumento_reconhecimento: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_cargo: Optional[str] = None
    contato_email: Optional[str] = None
    contato_telefone: Optional[str] = None


class LaboratorioCreate(LaboratorioBase):
    pass


class LaboratorioUpdate(BaseModel):
    nome: Optional[str] = None
    tipo: Optional[str] = None
    cnpj: Optional[str] = None
    endereco: Optional[str] = None
    cep: Optional[str] = None
    cidade: Optional[str] = None
    uf: Optional[str] = None
    contato: Optional[str] = None
    instrumento_reconhecimento: Optional[str] = None
    contato_nome: Optional[str] = None
    contato_cargo: Optional[str] = None
    contato_email: Optional[str] = None
    contato_telefone: Optional[str] = None


class LaboratorioResponse(LaboratorioBase):
    model_config = ConfigDict(from_attributes=True)

    id: str


__all__ = [
    "LaboratorioBase",
    "LaboratorioCreate",
    "LaboratorioUpdate",
    "LaboratorioResponse",
]
