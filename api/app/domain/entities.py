from dataclasses import dataclass
from datetime import date
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: tuple[T, ...]
    next_cursor: str | None = None


@dataclass(frozen=True, slots=True)
class Curso:
    codigo: str
    nome: str


@dataclass(frozen=True, slots=True)
class Disciplina:
    codigo: str
    nome: str


@dataclass(frozen=True, slots=True)
class Curriculo:
    id: int
    curso_codigo: str
    ano_versao: int
    nome: str
    curriculo_corrente: bool
    periodos_ideais: int
    carga_horaria_total: int
    carga_horaria_extensao: int
    fonte_referencia: str


@dataclass(frozen=True, slots=True)
class ComponenteCurricular:
    id: int
    ppc_id: int
    disciplina_codigo: str | None
    semestre_recomendado: int
    ordem_semestre: int
    tipo_componente: str
    nome_no_ppc: str
    disciplina_nome: str | None
    carga_horaria: int


@dataclass(frozen=True, slots=True)
class Docente:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class OfertaTurma:
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
    docentes: tuple[Docente, ...]


@dataclass(frozen=True, slots=True)
class PeriodoAcademico:
    ano: int
    semestre: int


@dataclass(frozen=True, slots=True)
class ItemHistoricoEscolar:
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


@dataclass(frozen=True, slots=True)
class SignupCommand:
    nome: str
    matricula: str
    email: str
    data_nascimento: date
    curso_codigo: str
    senha: str


@dataclass(frozen=True, slots=True)
class AuthUser:
    id: UUID
    email: str


@dataclass(frozen=True, slots=True)
class AuthSession:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


@dataclass(frozen=True, slots=True)
class UserProfile:
    id: UUID
    matricula: str
    curso_codigo: str
    nome: str


@dataclass(frozen=True, slots=True)
class SignupResult:
    usuario: AuthUser
    sessao: AuthSession | None
    confirmacao_email_necessaria: bool
    perfil: UserProfile | None = None


@dataclass(frozen=True, slots=True)
class LoginResult:
    usuario: AuthUser
    sessao: AuthSession
    perfil: UserProfile | None = None
