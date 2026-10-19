from pydantic import BaseModel, ConfigDict
from decimal import Decimal


class RelatorioResumoSummary(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_programas": 5,
                "total_inspecoes": 1234,
                "total_municipios": 12,
                "total_suspeitas": 10,
                "total_focos": 2
            }
        }
    )
    
    total_programas: int
    total_inspecoes: int
    total_municipios: int
    total_suspeitas: int = 0
    total_focos: int = 0
