from dataclasses import dataclass
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True)
class Professor:
    id: UUID
    nome: str


@dataclass(frozen=True)
class TurmaProfessor:
    id: UUID
    disciplina_codigo: str
    disciplina: str
    ano: int
    semestre: int
    codigo_turma: str
    total_matriculas: int
    aprovados: int
    reprovados: int
    total_docentes: int


class ProfessoresRepository(Protocol):
    async def buscar(self, nome: str, limite: int, inicio: int) -> list[Professor]: ...
    async def obter(self, professor_id: UUID) -> Professor | None: ...
    async def turmas(self, professor_id: UUID) -> list[TurmaProfessor]: ...
