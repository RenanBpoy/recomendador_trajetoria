from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class QuestionarioRespostaRequest(BaseModel):
    valor: int = Field(ge=1, le=10)


class QuestionarioPerguntaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    ordem_global: int
    ordem_secao: int
    texto: str
    resposta: int | None = None


class QuestionarioSecaoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    ordem: int
    titulo: str
    descricao: str
    orientacao: str | None = None
    perguntas: list[QuestionarioPerguntaOut]


class QuestionarioPreenchimentoOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID | None
    status: Literal["NAO_INICIADO", "EM_ANDAMENTO", "CONCLUIDO"]
    total_perguntas: int
    total_respondidas: int
    atualizado_em: datetime | None = None
    concluido_em: datetime | None = None


class QuestionarioAtualOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    codigo: str
    versao: int
    titulo: str
    descricao: str
    escala_minima: int
    escala_maxima: int
    secoes: list[QuestionarioSecaoOut]
    preenchimento: QuestionarioPreenchimentoOut
