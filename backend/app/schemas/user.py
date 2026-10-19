from pydantic import BaseModel, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserLoginResponse(BaseModel):
    """Resposta após login — inclui todos os campos relevantes do usuário."""
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
