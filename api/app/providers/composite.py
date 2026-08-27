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
)
from app.domain.ports import AcademicDataProvider, HistoricoImportadoRepository


class CompositeAcademicDataProvider:
    """Combina a fonte acadêmica principal com históricos enviados pelos alunos."""

    def __init__(
        self,
        primary: AcademicDataProvider,
        imported_histories: HistoricoImportadoRepository,
    ) -> None:
        self._primary = primary
        self._imported_histories = imported_histories

    async def list_courses(self, *, limit: int, cursor: str | None = None) -> Page[Curso]:
        return await self._primary.list_courses(limit=limit, cursor=cursor)

    async def get_course(self, codigo: str) -> Curso | None:
        return await self._primary.get_course(codigo)

    async def list_curricula(self, curso_codigo: str) -> tuple[Curriculo, ...]:
        return await self._primary.list_curricula(curso_codigo)

    async def get_curriculum(self, ppc_id: int) -> Curriculo | None:
        return await self._primary.get_curriculum(ppc_id)

    async def list_curriculum_components(
        self, ppc_id: int
    ) -> tuple[ComponenteCurricular, ...]:
        return await self._primary.list_curriculum_components(ppc_id)

    async def list_disciplines(
        self, *, limit: int, cursor: str | None = None
    ) -> Page[Disciplina]:
        return await self._primary.list_disciplines(limit=limit, cursor=cursor)

    async def get_discipline(self, codigo: str) -> Disciplina | None:
        return await self._primary.get_discipline(codigo)

    async def list_class_offerings(
        self,
        *,
        limit: int,
        cursor: UUID | None = None,
        curso_codigo: str | None = None,
        disciplina_codigo: str | None = None,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> Page[OfertaTurma]:
        return await self._primary.list_class_offerings(
            limit=limit,
            cursor=cursor,
            curso_codigo=curso_codigo,
            disciplina_codigo=disciplina_codigo,
            ano=ano,
            semestre=semestre,
        )

    async def get_class_offering(self, offering_id: UUID) -> OfertaTurma | None:
        return await self._primary.get_class_offering(offering_id)

    async def list_academic_periods(self) -> tuple[PeriodoAcademico, ...]:
        return await self._primary.list_academic_periods()

    async def get_school_history(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...] | None:
        primary = await self._primary.get_school_history(matricula)
        if primary is None:
            return None
        imported = await self._imported_histories.get_by_student(matricula)
        return tuple(
            sorted(
                (*primary, *imported),
                key=lambda item: (
                    item.ano,
                    item.semestre,
                    item.disciplina,
                    item.fonte,
                ),
            )
        )
