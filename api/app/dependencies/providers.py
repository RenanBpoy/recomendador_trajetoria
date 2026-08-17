from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.domain.ports import AcademicDataProvider
from app.providers.postgres import PostgresAcademicDataProvider
from app.repositories.postgres import (
    SqlAlchemyCurriculoRepository,
    SqlAlchemyCursoRepository,
    SqlAlchemyDisciplinaRepository,
    SqlAlchemyHistoricoEscolarRepository,
    SqlAlchemyOfertaTurmaRepository,
)
from app.services.academic import (
    CurriculoService,
    CursoService,
    DisciplinaService,
    HistoricoEscolarService,
    OfertaTurmaService,
)

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


async def get_academic_provider(session: DatabaseSession) -> AcademicDataProvider:
    return PostgresAcademicDataProvider(
        courses=SqlAlchemyCursoRepository(session),
        curricula=SqlAlchemyCurriculoRepository(session),
        disciplines=SqlAlchemyDisciplinaRepository(session),
        offerings=SqlAlchemyOfertaTurmaRepository(session),
        histories=SqlAlchemyHistoricoEscolarRepository(session),
    )


AcademicProvider = Annotated[AcademicDataProvider, Depends(get_academic_provider)]


def get_course_service(provider: AcademicProvider) -> CursoService:
    return CursoService(provider)


def get_curriculum_service(provider: AcademicProvider) -> CurriculoService:
    return CurriculoService(provider)


def get_discipline_service(provider: AcademicProvider) -> DisciplinaService:
    return DisciplinaService(provider)


def get_class_offering_service(provider: AcademicProvider) -> OfertaTurmaService:
    return OfertaTurmaService(provider)


def get_school_history_service(provider: AcademicProvider) -> HistoricoEscolarService:
    return HistoricoEscolarService(provider)


CursoServiceDep = Annotated[CursoService, Depends(get_course_service)]
CurriculoServiceDep = Annotated[CurriculoService, Depends(get_curriculum_service)]
DisciplinaServiceDep = Annotated[DisciplinaService, Depends(get_discipline_service)]
OfertaTurmaServiceDep = Annotated[
    OfertaTurmaService, Depends(get_class_offering_service)
]
HistoricoEscolarServiceDep = Annotated[
    HistoricoEscolarService, Depends(get_school_history_service)
]
