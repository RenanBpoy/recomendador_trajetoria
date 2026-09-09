from uuid import UUID
from pydantic import BaseModel
from app.schemas.academic import DisciplinaResponse, OfertaTurmaResponse
from app.schemas.professores import EstatisticasProfessorOut


class BuscaDisciplinasOut(BaseModel):
    itens: list[DisciplinaResponse]
    tem_mais: bool


class TurmaDiarioOut(BaseModel):
    id: UUID
    ano: int
    semestre: int
    codigo_turma: str
    curso_codigo: str
    carga_horaria: int


class ConsultaDisciplinaOut(EstatisticasProfessorOut):
    codigo: str
    nome: str
    cargas_horarias: list[int]
    turmas: list[TurmaDiarioOut]


class RegistroDiarioOut(BaseModel):
    nome: str
    matricula: str
    curso_aluno_codigo: str
    numero_lista: int
    faltas_total: int
    media_parcial: float | None
    media_final: float | None
    situacao_final: str


class DiarioClasseOut(EstatisticasProfessorOut):
    oferta: OfertaTurmaResponse
    acesso_completo: bool
    registros: list[RegistroDiarioOut]
