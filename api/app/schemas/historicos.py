from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class HistoricoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ItemImportacaoHistoricoResponse(HistoricoSchema):
    id: int
    codigo_original: str
    nome_original: str
    carga_horaria: int
    ano: int
    semestre: int
    situacao: str
    media: float | None
    correspondencia_id: int | None
    disciplina_codigo: str | None
    disciplina_nome: str | None
    metodo_correspondencia: str | None
    confianca_correspondencia: float | None
    status_correspondencia: str | None


class ImportacaoHistoricoResponse(HistoricoSchema):
    id: UUID
    nome_arquivo: str
    criado_em: datetime
    curso_codigo_documento: str
    ppc_ano_documento: int
    ppc_referencia_id: int
    total_itens: int
    identificados: int
    requerem_confirmacao: int
    nao_identificados: int
    itens: tuple[ItemImportacaoHistoricoResponse, ...]


class RevisarCorrespondenciaRequest(BaseModel):
    acao: Literal["confirmar", "rejeitar"]


class CandidatoEquivalenciaResponse(HistoricoSchema):
    id: int
    codigo_original: str
    nome_original: str
    carga_horaria: int
    ano: int
    semestre: int
    situacao: str
    media: float | None
    selecionavel: bool
    motivo_indisponibilidade: str | None
    similaridade_nome: float | None
    em_uso: bool
    componente_em_uso_id: int | None
    slot_em_uso: int | None


class EquivalenciaManualResponse(HistoricoSchema):
    id: int
    ppc_id: int
    ppc_componente_id: int
    slot_ordem: int
    historico_item_id: int
    codigo_original: str
    nome_original: str
    carga_horaria: int
    ano: int
    semestre: int
    situacao: str
    media: float | None
    tipo_componente: str
    nome_componente: str
    disciplina_codigo: str | None


class SalvarEquivalenciaManualRequest(BaseModel):
    historico_item_id: int
