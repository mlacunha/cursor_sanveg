from pydantic import BaseModel, ConfigDict, Field


class MunicipioResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    nome: str
    uf_id: int = Field(validation_alias="estado_id")
