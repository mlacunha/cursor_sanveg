from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class InspecaoFotoCreate(BaseModel):
    """Payload interno gerado após o upload — não é exposto diretamente ao cliente."""
    id: str
    id_area_programa: str
    arquivo_nome: str
    arquivo_path: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_captura: Optional[datetime] = None
    descricao: Optional[str] = None


class InspecaoFotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    id_area_programa: str
    arquivo_nome: str
    arquivo_path: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_captura: Optional[datetime] = None
    descricao: Optional[str] = None
    # Campo derivado conveniente para o cliente
    exif_extraido: bool = False


class InspecaoFotoUploadResponse(BaseModel):
    """Retorno do endpoint de upload com metadados extraídos."""
    id: str
    arquivo_nome: str
    arquivo_path: str
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    data_captura: Optional[datetime] = None
    exif_extraido: bool
    message: str
