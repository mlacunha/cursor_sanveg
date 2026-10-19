from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class ImportJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    estado_sigla: Optional[str]
    status: str
    force_reload: bool
    created_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    total: Optional[int]
    existing: Optional[int]
    new: Optional[int]
    error: Optional[str]
