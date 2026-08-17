from uuid import UUID

from app.core.errors import ResourceNotFoundError
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
from app.domain.ports import AcademicDataProvider


class CursoService:
    def __init__(self, provider: AcademicDataProvider) -> None:
        self._provider = provider

    async def list(self, *, limit: int, cursor: str | None = None) -> Page[Curso]:
        return await self._provider.list_courses(limit=limit, cursor=cursor)

    async def get(self, codigo: str) -> Curso:
        course = await self._provider.get_course(codigo)
        if course is None:
            raise ResourceNotFoundError("Curso", codigo)
        return course

    async def list_curricula(self, codigo: str) -> tuple[Curriculo, ...]:
        await self.get(codigo)
        return await self._provider.list_curricula(codigo)


class CurriculoService:
    def __init__(self, provider: AcademicDataProvider) -> None:
        self._provider = provider

    async def get(self, ppc_id: int) -> Curriculo:
        curriculum = await self._provider.get_curriculum(ppc_id)
        if curriculum is None:
            raise ResourceNotFoundError("PPC", ppc_id)
        return curriculum

    async def list_components(self, ppc_id: int) -> tuple[ComponenteCurricular, ...]:
        await self.get(ppc_id)
        return await self._provider.list_curriculum_components(ppc_id)


class DisciplinaService:
    def __init__(self, provider: AcademicDataProvider) -> None:
        self._provider = provider

    async def list(self, *, limit: int, cursor: str | None = None) -> Page[Disciplina]:
        return await self._provider.list_disciplines(limit=limit, cursor=cursor)

    async def get(self, codigo: str) -> Disciplina:
        discipline = await self._provider.get_discipline(codigo)
        if discipline is None:
            raise ResourceNotFoundError("Disciplina", codigo)
        return discipline


class OfertaTurmaService:
    def __init__(self, provider: AcademicDataProvider) -> None:
        self._provider = provider

    async def list(
        self,
        *,
        limit: int,
        cursor: UUID | None = None,
        curso_codigo: str | None = None,
        disciplina_codigo: str | None = None,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> Page[OfertaTurma]:
        return await self._provider.list_class_offerings(
            limit=limit,
            cursor=cursor,
            curso_codigo=curso_codigo,
            disciplina_codigo=disciplina_codigo,
            ano=ano,
            semestre=semestre,
        )

    async def get(self, offering_id: UUID) -> OfertaTurma:
        offering = await self._provider.get_class_offering(offering_id)
        if offering is None:
            raise ResourceNotFoundError("Oferta de turma", offering_id)
        return offering

    async def list_periods(self) -> tuple[PeriodoAcademico, ...]:
        return await self._provider.list_academic_periods()


class HistoricoEscolarService:
    def __init__(self, provider: AcademicDataProvider) -> None:
        self._provider = provider

    async def get(self, matricula: str) -> tuple[ItemHistoricoEscolar, ...]:
        history = await self._provider.get_school_history(matricula)
        if history is None:
            raise ResourceNotFoundError("Aluno", matricula)
        return history
