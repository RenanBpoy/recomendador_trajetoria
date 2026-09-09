from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ProfessorOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    nome: str


class BuscaProfessoresOut(BaseModel):
    itens: list[ProfessorOut]
    tem_mais: bool


class EstatisticasProfessorOut(BaseModel):
    aprovados: int
    reprovados: int
    outros_resultados: int
    resultados_avaliados: int
    taxa_aprovacao: float | None


class TurmaProfessorOut(EstatisticasProfessorOut):
    id: UUID
    ano: int
    semestre: int
    codigo_turma: str
    compartilhada: bool


class DisciplinaProfessorOut(EstatisticasProfessorOut):
    codigo: str
    nome: str
    turmas: list[TurmaProfessorOut]


class PerfilProfessorOut(ProfessorOut, EstatisticasProfessorOut):
    total_turmas: int
    disciplinas: list[DisciplinaProfessorOut]
