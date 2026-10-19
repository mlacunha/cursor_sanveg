from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class PropriedadeInlineProduto(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    nome: str


class ProdutoCreate(BaseModel):
    id_propriedade: str
    produto: str


class ProdutoUpdate(BaseModel):
    id_propriedade: Optional[str] = None
    produto: Optional[str] = None


class ProdutoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    id_propriedade: str
    produto: str
    criado_em: datetime
    atualizado_em: datetime
    propriedade_data: Optional[PropriedadeInlineProduto] = None
