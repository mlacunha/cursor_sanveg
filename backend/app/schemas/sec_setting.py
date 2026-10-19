from pydantic import BaseModel, ConfigDict
from typing import Optional


class SecSettingCreate(BaseModel):
    set_name: str
    set_value: Optional[str] = None


class SecSettingUpdate(BaseModel):
    set_value: Optional[str] = None


class SecSettingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    set_name: str
    set_value: Optional[str] = None
