from typing import Annotated
from fastapi import Depends
from app.dependencies.auth import DatabaseSession
from app.repositories.professores import SqlAlchemyProfessoresRepository
from app.services.professores import ProfessoresService


def get_professores_service(session: DatabaseSession) -> ProfessoresService:
    return ProfessoresService(SqlAlchemyProfessoresRepository(session))


ProfessoresServiceDep = Annotated[ProfessoresService, Depends(get_professores_service)]
