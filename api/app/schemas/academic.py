from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DomainSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CursoResponse(DomainSchema):
    codigo: str
    nome: str


class DisciplinaResponse(DomainSchema):
    codigo: str
    nome: str


class CurriculoResponse(DomainSchema):
    id: int
    curso_codigo: str
    ano_versao: int
    nome: str
    curriculo_corrente: bool
    periodos_ideais: int
    carga_horaria_total: int
    carga_horaria_extensao: int
    fonte_referencia: str


class ComponenteCurricularResponse(DomainSchema):
    id: int
    ppc_id: int
    disciplina_codigo: str | None
    semestre_recomendado: int
    ordem_semestre: int
    tipo_componente: str
    nome_no_ppc: str
    disciplina_nome: str | None
    carga_horaria: int


class DocenteResponse(DomainSchema):
    id: UUID
    nome: str


class OfertaTurmaResponse(DomainSchema):
    id: UUID
    curso_codigo: str
    curso_nome: str
    disciplina_codigo: str
    disciplina_nome: str
    ano: int
    semestre: int
    codigo_turma: str
    carga_horaria: int
    creditos: int
    situacao: str
    docentes: tuple[DocenteResponse, ...]


class PeriodoAcademicoResponse(DomainSchema):
    ano: int
    semestre: int


class ItemHistoricoEscolarResponse(DomainSchema):
    matricula: str
    disciplina_codigo: str
    disciplina: str
    professores: str | None
    ano: int
    semestre: int
    codigo_turma: str
    media_final: float | None
    faltas_total: int
    situacao_final: str


class StatusResponse(BaseModel):
    status: str
    service: str
