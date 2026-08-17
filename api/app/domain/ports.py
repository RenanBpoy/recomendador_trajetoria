from typing import Protocol
from uuid import UUID

from app.domain.entities import (
    ComponenteCurricular,
    Curriculo,
    Curso,
    Disciplina,
    ItemHistoricoEscolar,
    OfertaTurma,
    Page,
    PeriodoAcademico,
    LoginResult,
    SignupCommand,
    SignupResult,
    UserProfile,
)


class CursoRepository(Protocol):
    async def list(self, *, limit: int, cursor: str | None = None) -> Page[Curso]: ...
    async def get(self, codigo: str) -> Curso | None: ...


class CurriculoRepository(Protocol):
    async def list_by_course(self, curso_codigo: str) -> tuple[Curriculo, ...]: ...
    async def get(self, ppc_id: int) -> Curriculo | None: ...
    async def list_components(self, ppc_id: int) -> tuple[ComponenteCurricular, ...]: ...


class DisciplinaRepository(Protocol):
    async def list(self, *, limit: int, cursor: str | None = None) -> Page[Disciplina]: ...
    async def get(self, codigo: str) -> Disciplina | None: ...


class OfertaTurmaRepository(Protocol):
    async def list(
        self,
        *,
        limit: int,
        cursor: UUID | None = None,
        curso_codigo: str | None = None,
        disciplina_codigo: str | None = None,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> Page[OfertaTurma]: ...
    async def get(self, offering_id: UUID) -> OfertaTurma | None: ...
    async def list_periods(self) -> tuple[PeriodoAcademico, ...]: ...


class HistoricoEscolarRepository(Protocol):
    async def get_by_student(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...] | None: ...


class UserRegistrationRepository(Protocol):
    async def student_exists(self, matricula: str) -> bool: ...
    async def course_exists(self, codigo: str) -> bool: ...
    async def registration_in_use(self, matricula: str) -> bool: ...
    async def get_profile(self, user_id: UUID) -> UserProfile | None: ...


class AuthProvider(Protocol):
    async def signup(self, command: SignupCommand) -> SignupResult: ...
    async def login(self, *, email: str, password: str) -> LoginResult: ...


class AcademicDataProvider(Protocol):
    async def list_courses(self, *, limit: int, cursor: str | None = None) -> Page[Curso]: ...
    async def get_course(self, codigo: str) -> Curso | None: ...
    async def list_curricula(self, curso_codigo: str) -> tuple[Curriculo, ...]: ...
    async def get_curriculum(self, ppc_id: int) -> Curriculo | None: ...
    async def list_curriculum_components(
        self, ppc_id: int
    ) -> tuple[ComponenteCurricular, ...]: ...
    async def list_disciplines(
        self, *, limit: int, cursor: str | None = None
    ) -> Page[Disciplina]: ...
    async def get_discipline(self, codigo: str) -> Disciplina | None: ...
    async def list_class_offerings(
        self,
        *,
        limit: int,
        cursor: UUID | None = None,
        curso_codigo: str | None = None,
        disciplina_codigo: str | None = None,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> Page[OfertaTurma]: ...
    async def get_class_offering(self, offering_id: UUID) -> OfertaTurma | None: ...
    async def list_academic_periods(self) -> tuple[PeriodoAcademico, ...]: ...
    async def get_school_history(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...] | None: ...
