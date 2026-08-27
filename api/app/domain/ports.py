from datetime import date
from typing import Protocol
from uuid import UUID

from app.domain.entities import (
    CandidatoEquivalencia,
    ComponenteCurricular,
    AuthUser,
    Curriculo,
    Curso,
    Disciplina,
    ItemHistoricoEscolar,
    HistoricoDocumento,
    ImportacaoHistorico,
    CorrespondenciaProposta,
    OfertaTurma,
    Page,
    PeriodoAcademico,
    LoginResult,
    SignupCommand,
    SignupResult,
    UserProfile,
    EquivalenciaManual,
    PlanoSemanaItem,
    PlanoSemanaItemInput,
    QuestionarioAtual,
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


class HistoricoImportadoRepository(Protocol):
    async def get_by_student(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...]: ...


class HistoricoImportacaoRepository(Protocol):
    async def replace_active(
        self,
        *,
        usuario_id: UUID,
        nome_arquivo: str,
        hash_arquivo: str,
        documento: HistoricoDocumento,
        ppc_referencia_id: int,
        correspondencias: tuple[CorrespondenciaProposta, ...],
    ) -> ImportacaoHistorico: ...

    async def get_active(self, usuario_id: UUID) -> ImportacaoHistorico | None: ...

    async def review_correspondence(
        self, *, usuario_id: UUID, correspondencia_id: int, action: str
    ) -> ImportacaoHistorico | None: ...


class EquivalenciaManualRepository(Protocol):
    async def list_candidates(
        self, *, usuario_id: UUID, ppc_id: int
    ) -> tuple[CandidatoEquivalencia, ...]: ...

    async def list_mappings(
        self, *, usuario_id: UUID, ppc_id: int
    ) -> tuple[EquivalenciaManual, ...]: ...

    async def save(
        self,
        *,
        usuario_id: UUID,
        ppc_id: int,
        ppc_componente_id: int,
        slot_ordem: int,
        historico_item_id: int,
    ) -> EquivalenciaManual: ...

    async def delete(
        self,
        *,
        usuario_id: UUID,
        ppc_id: int,
        ppc_componente_id: int,
        slot_ordem: int,
    ) -> bool: ...


class HistoricoDocumentoProvider(Protocol):
    def read(self, content: bytes) -> HistoricoDocumento: ...


class UserRegistrationRepository(Protocol):
    async def student_exists(self, matricula: str) -> bool: ...
    async def course_exists(self, codigo: str) -> bool: ...
    async def registration_in_use(self, matricula: str) -> bool: ...
    async def get_profile(self, user_id: UUID) -> UserProfile | None: ...
    async def select_curriculum(
        self, *, user_id: UUID, ppc_id: int
    ) -> UserProfile | None: ...
    async def update_personal_data(
        self, *, user_id: UUID, nome: str, data_nascimento: date
    ) -> UserProfile | None: ...
    async def update_avatar(
        self, *, user_id: UUID, avatar_path: str | None
    ) -> UserProfile | None: ...


class AuthProvider(Protocol):
    async def signup(self, command: SignupCommand) -> SignupResult: ...
    async def login(self, *, email: str, password: str) -> LoginResult: ...
    async def get_user(self, access_token: str) -> AuthUser: ...
    async def update_email(self, *, access_token: str, email: str) -> AuthUser: ...
    async def update_password(self, *, access_token: str, password: str) -> None: ...


class AvatarStorageProvider(Protocol):
    async def upload(
        self,
        *,
        user_id: UUID,
        access_token: str,
        content: bytes,
        content_type: str,
    ) -> str: ...
    async def delete(self, *, path: str, access_token: str) -> None: ...
    async def create_signed_url(
        self, *, path: str, access_token: str
    ) -> str: ...


class PlanoSemanalRepository(Protocol):
    async def list_by_user(self, user_id: UUID) -> tuple[PlanoSemanaItem, ...]: ...
    async def replace_for_user(
        self, *, user_id: UUID, items: tuple[PlanoSemanaItemInput, ...]
    ) -> tuple[PlanoSemanaItem, ...]: ...


class QuestionarioRepository(Protocol):
    async def get_active(self, user_id: UUID) -> QuestionarioAtual | None: ...
    async def save_answer(
        self,
        *,
        user_id: UUID,
        questionario_id: int,
        pergunta_id: int,
        valor: int,
    ) -> None: ...
    async def complete(self, *, user_id: UUID, questionario_id: int) -> None: ...


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
