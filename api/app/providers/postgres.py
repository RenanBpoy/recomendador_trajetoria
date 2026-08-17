from uuid import UUID

from app.domain.entities import ComponenteCurricular, Curriculo, Curso, Disciplina, ItemHistoricoEscolar, OfertaTurma, Page, PeriodoAcademico
from app.domain.ports import CurriculoRepository, CursoRepository, DisciplinaRepository, HistoricoEscolarRepository, OfertaTurmaRepository


class PostgresAcademicDataProvider:
    """Normaliza o banco atual no contrato acadêmico usado pelos services."""

    def __init__(self, courses: CursoRepository, curricula: CurriculoRepository, disciplines: DisciplinaRepository, offerings: OfertaTurmaRepository, histories: HistoricoEscolarRepository) -> None:
        self._courses = courses
        self._curricula = curricula
        self._disciplines = disciplines
        self._offerings = offerings
        self._histories = histories

    async def list_courses(self, *, limit: int, cursor: str | None = None) -> Page[Curso]:
        return await self._courses.list(limit=limit, cursor=cursor)

    async def get_course(self, codigo: str) -> Curso | None:
        return await self._courses.get(codigo)

    async def list_curricula(self, curso_codigo: str) -> tuple[Curriculo, ...]:
        return await self._curricula.list_by_course(curso_codigo)

    async def get_curriculum(self, ppc_id: int) -> Curriculo | None:
        return await self._curricula.get(ppc_id)

    async def list_curriculum_components(self, ppc_id: int) -> tuple[ComponenteCurricular, ...]:
        return await self._curricula.list_components(ppc_id)

    async def list_disciplines(self, *, limit: int, cursor: str | None = None) -> Page[Disciplina]:
        return await self._disciplines.list(limit=limit, cursor=cursor)

    async def get_discipline(self, codigo: str) -> Disciplina | None:
        return await self._disciplines.get(codigo)

    async def list_class_offerings(self, *, limit: int, cursor: UUID | None = None, curso_codigo: str | None = None, disciplina_codigo: str | None = None, ano: int | None = None, semestre: int | None = None) -> Page[OfertaTurma]:
        return await self._offerings.list(limit=limit, cursor=cursor, curso_codigo=curso_codigo, disciplina_codigo=disciplina_codigo, ano=ano, semestre=semestre)

    async def get_class_offering(self, offering_id: UUID) -> OfertaTurma | None:
        return await self._offerings.get(offering_id)

    async def list_academic_periods(self) -> tuple[PeriodoAcademico, ...]:
        return await self._offerings.list_periods()

    async def get_school_history(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...] | None:
        return await self._histories.get_by_student(matricula)
