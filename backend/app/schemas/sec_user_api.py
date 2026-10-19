from pydantic import BaseModel, ConfigDict
from typing import Optional


class SecUserApiCreate(BaseModel):
    login: str
    pswd: str
    name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[str] = 'Y'


class SecUserApiUpdate(BaseModel):
    pswd: Optional[str] = None
    name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[str] = None


class SecUserApiResponse(BaseModel):
    """Response - NÃO inclui pswd (senha) por segurança"""
    model_config = ConfigDict(from_attributes=True)
    login: str
    name: Optional[str] = None
    email: Optional[str] = None
    active: Optional[str] = None
