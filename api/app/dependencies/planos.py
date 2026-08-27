from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import DatabaseSession
from app.repositories.planos import SqlAlchemyPlanoSemanalRepository
from app.services.planos import PlanoSemanalService


def get_weekly_plan_service(session: DatabaseSession) -> PlanoSemanalService:
    return PlanoSemanalService(SqlAlchemyPlanoSemanalRepository(session))


PlanoSemanalServiceDep = Annotated[
    PlanoSemanalService, Depends(get_weekly_plan_service)
]
