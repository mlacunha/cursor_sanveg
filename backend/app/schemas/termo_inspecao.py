from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class UserInlineTermoInspecao(BaseModel):
    model_config = {"from_attributes": True}
    id: str
    login: Optional[str] = None
    nome: Optional[str] = None
    email: Optional[str] = None


# Schema inline para Propriedade
class PropriedadeInlineTermoInspecao(BaseModel):
    id: str
    nome: str
    municipio: Optional[str] = None
    UF: Optional[str] = None

    model_config = {"from_attributes": True}


# Schema para criação de termo de inspeção
class TermoInspecaoCreate(BaseModel):
    data: datetime = Field(..., description="Data do termo (obrigatório)")
    termo_coleta: Optional[int] = None
    id_usuario: str = Field(..., description="ID do usuário (obrigatório)")
    id_propriedade: str = Field(
        ...,
        description="ID da propriedade (obrigatório)"
    )


# Schema para atualização parcial (PATCH)
class TermoInspecaoUpdate(BaseModel):
    data: Optional[datetime] = None
    ficha_inspecao: Optional[int] = None
    termo_coleta: Optional[int] = None
    id_usuario: Optional[str] = None
    id_propriedade: Optional[str] = None


# Schema de resposta
class TermoInspecaoResponse(BaseModel):
    id: str
    data: datetime
    ficha_inspecao: Optional[int] = None
    termo_coleta: Optional[int] = None
    id_usuario: str
    id_propriedade: str
    criado_em: datetime
    atualizado_em: datetime
    
    # Dados relacionados - opcionais
    usuario_data: Optional[UserInlineTermoInspecao] = None
    propriedade_data: Optional[PropriedadeInlineTermoInspecao] = None

    model_config = {"from_attributes": True}
