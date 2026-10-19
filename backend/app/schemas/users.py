from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional
from datetime import datetime


class OrgaoInlineUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sigla: str
    nome: str


class UnidadeInlineUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str


class CargoInlineUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    sigla: Optional[str] = None
    nome: str


class FormacaoInlineUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str


class UserCreate(BaseModel):
    login: str
    password: str
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    matricula: Optional[str] = None
    carteirafiscal: Optional[str] = None
    active: Optional[bool] = True
    role: Optional[str] = 'comum'  # 'comum' | 'admin' | 'superusuario'
    id_orgao: Optional[str] = None
    id_unidade: Optional[str] = None
    id_cargo: Optional[str] = None
    id_formacao: Optional[str] = None


class UserUpdate(BaseModel):
    password: Optional[str] = None
    nome: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    matricula: Optional[str] = None
    carteirafiscal: Optional[str] = None
    active: Optional[bool] = None
    role: Optional[str] = None
    id_orgao: Optional[str] = None
    id_unidade: Optional[str] = None
    id_cargo: Optional[str] = None
    id_formacao: Optional[str] = None


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    login: str
    nome: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None
    telefone: Optional[str] = None
    matricula: Optional[str] = None
    carteirafiscal: Optional[str] = None
    active: Optional[bool] = None
    role: Optional[str] = None
    id_orgao: Optional[str] = None
    id_unidade: Optional[str] = None
    id_cargo: Optional[str] = None
    id_formacao: Optional[str] = None
    criado_em: Optional[datetime] = None
    atualizado_em: Optional[datetime] = None

    orgao_data: Optional[OrgaoInlineUser] = None
    unidade_data: Optional[UnidadeInlineUser] = None
    cargo_data: Optional[CargoInlineUser] = None
    formacao_data: Optional[FormacaoInlineUser] = None
