from datetime import time
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class PlanoSemanaItemInputSchema(BaseModel):
    tipo_atividade: Literal["DISCIPLINA", "ESTAGIO", "OUTRO"]
    titulo: str = Field(min_length=1, max_length=120)
    dia_semana: int = Field(ge=1, le=5)
    hora_inicio: time
    hora_fim: time
    observacoes: str | None = Field(default=None, max_length=500)

    @field_validator("titulo")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        return value.strip()

    @field_validator("observacoes")
    @classmethod
    def normalize_notes(cls, value: str | None) -> str | None:
        normalized = value.strip() if value else None
        return normalized or None

    @model_validator(mode="after")
    def validate_period(self) -> Self:
        if self.hora_fim <= self.hora_inicio:
            raise ValueError("O horário final deve ser posterior ao horário inicial.")
        return self


class PlanoSemanaReplaceRequest(BaseModel):
    itens: list[PlanoSemanaItemInputSchema] = Field(max_length=100)


class PlanoSemanaItemOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_atividade: str
    titulo: str
    dia_semana: int
    hora_inicio: time
    hora_fim: time
    observacoes: str | None = None
