from pydantic import BaseModel, ConfigDict
from typing import Optional


class DashboardFiltrosCreate(BaseModel):
    ano: Optional[int] = None
    trimestre: Optional[int] = None
    id_programa: Optional[str] = None
    municipio: Optional[str] = None


class DashboardFiltrosUpdate(BaseModel):
    ano: Optional[int] = None
    trimestre: Optional[int] = None
    id_programa: Optional[str] = None
    municipio: Optional[str] = None


class DashboardFiltrosResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    ano: Optional[int] = None
    trimestre: Optional[int] = None
    id_programa: Optional[str] = None
    municipio: Optional[str] = None
