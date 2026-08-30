from datetime import time
from uuid import UUID
from unicodedata import combining, normalize

from app.core.errors import ApplicationError, ResourceNotFoundError
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

    async def list_available_discipline_offerings(
        self,
        matricula: str,
        *,
        ano: int,
        semestre: int,
        dia_semana: int,
        hora_inicio: time,
        hora_fim: time,
    ) -> tuple[OfertaTurma, ...]:
        """Lista ofertas não aprovadas que coincidem com o intervalo solicitado."""

        if hora_fim <= hora_inicio:
            raise ApplicationError(
                "O fim do intervalo deve ser posterior ao início.",
                code="intervalo_horario_invalido",
            )

        approved = await self._provider.get_approved_discipline_codes(matricula)
        if approved is None:
            raise ResourceNotFoundError("Aluno", matricula)
        approved_codes = {code.strip().upper() for code in approved}

        offerings: dict[UUID, OfertaTurma] = {}
        cursor: UUID | None = None
        visited_cursors: set[str] = set()
        while True:
            page = await self._provider.list_class_offerings(
                limit=100,
                cursor=cursor,
                ano=ano,
                semestre=semestre,
            )
            for offering in page.items:
                code = offering.disciplina_codigo.strip().upper()
                matches_interval = any(
                    schedule.dia_semana == dia_semana
                    and schedule.hora_inicio < hora_fim
                    and hora_inicio < schedule.hora_fim
                    for schedule in offering.horarios
                )
                if code not in approved_codes and matches_interval:
                    offerings[offering.id] = offering

            if page.next_cursor is None or page.next_cursor in visited_cursors:
                break
            visited_cursors.add(page.next_cursor)
            cursor = UUID(page.next_cursor)

        return tuple(
            sorted(
                offerings.values(),
                key=lambda offering: (
                    self._normalized_text(offering.disciplina_nome),
                    offering.disciplina_codigo,
                    offering.codigo_turma,
                ),
            )
        )

    @staticmethod
    def _normalized_text(value: str) -> str:
        return "".join(
            char
            for char in normalize("NFD", value.lower())
            if not combining(char)
        )
