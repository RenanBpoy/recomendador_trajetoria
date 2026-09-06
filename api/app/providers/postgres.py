from uuid import UUID
from unicodedata import combining, normalize

from app.domain.entities import ComponenteCurricular, Curriculo, Curso, DedicacaoExtraclasseDisciplina, Disciplina, DisciplinaEquivalencia, EstatisticaDisciplina, ItemHistoricoEscolar, OfertaTurma, Page, PeriodoAcademico
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

    async def list_discipline_equivalences(
        self,
    ) -> tuple[DisciplinaEquivalencia, ...]:
        return await self._disciplines.list_equivalences()

    async def get_discipline_statistics(
        self,
        codigos: tuple[str, ...],
        *,
        excluir_matricula: str | None = None,
    ) -> tuple[EstatisticaDisciplina, ...]:
        return await self._disciplines.get_statistics(
            codigos,
            excluir_matricula=excluir_matricula,
        )

    async def get_discipline_extraclass_dedications(
        self, codigos: tuple[str, ...]
    ) -> tuple[DedicacaoExtraclasseDisciplina, ...]:
        return await self._disciplines.get_extraclass_dedications(codigos)

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

    async def get_approved_discipline_codes(
        self,
        matricula: str,
    ) -> tuple[str, ...] | None:
        history = await self._histories.get_by_student(matricula)
        if history is None:
            return None
        return tuple(
            sorted(
                {
                    item.disciplina_codigo.strip().upper()
                    for item in history
                    if self._is_approved(item.situacao_final)
                }
            )
        )

    @staticmethod
    def _is_approved(status: str) -> bool:
        normalized = "".join(
            char
            for char in normalize("NFD", status.lower())
            if not combining(char)
        )
        return any(
            marker in normalized
            for marker in ("aprovado", "dispensado", "dispensa", "aproveitamento")
        )
