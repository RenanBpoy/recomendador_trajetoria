from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import DatabaseSession
from app.repositories.primeiro_acesso import SqlAlchemyPrimeiroAcessoRepository
from app.services.primeiro_acesso import PrimeiroAcessoService


def get_first_access_service(session: DatabaseSession) -> PrimeiroAcessoService:
    return PrimeiroAcessoService(SqlAlchemyPrimeiroAcessoRepository(session))


PrimeiroAcessoServiceDep = Annotated[
    PrimeiroAcessoService, Depends(get_first_access_service)
]
