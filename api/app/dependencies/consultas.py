from typing import Annotated
from fastapi import Depends
from app.dependencies.auth import DatabaseSession
from app.dependencies.providers import AcademicProvider
from app.repositories.consultas import SqlAlchemyConsultasAcademicasRepository
from app.services.consultas import ConsultasAcademicasService


def get_consultas_service(session: DatabaseSession, provider: AcademicProvider):
    return ConsultasAcademicasService(SqlAlchemyConsultasAcademicasRepository(session), provider)


ConsultasServiceDep = Annotated[ConsultasAcademicasService, Depends(get_consultas_service)]
