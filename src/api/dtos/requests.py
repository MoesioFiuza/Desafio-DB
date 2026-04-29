from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class CreateDocumentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1, max_length=255)
    autor: str = Field(min_length=1, max_length=255)
    conteudo: str = Field(min_length=1)
    data: date
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
