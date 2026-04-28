from datetime import date

from pydantic import BaseModel, ConfigDict, Field, model_validator


class CreateDocumentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    titulo: str = Field(min_length=1, max_length=255)
    autor: str = Field(min_length=1, max_length=255)
    conteudo: str = Field(min_length=1)
    data: date
    latitude: float | None = Field(default=None, ge=-90.0, le=90.0)
    longitude: float | None = Field(default=None, ge=-180.0, le=180.0)

    @model_validator(mode="after")
    def validate_coordinate_pair(self) -> "CreateDocumentRequest":
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude e longitude devem ser informadas juntas.")
        return self
