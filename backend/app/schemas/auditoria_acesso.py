from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class AuditoriaAcessoCreate(BaseModel):
    id: str
    id_usuario: str
    recurso_acessado: str
    tipo_acao: str
    ip_origem: Optional[str] = None

class AuditoriaAcessoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_usuario: str
    recurso_acessado: str
    tipo_acao: str
    data_hora: datetime
    ip_origem: Optional[str] = None
