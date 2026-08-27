from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db_session
from app.dependencies.providers import AcademicProvider
from app.providers.historico_pdf_ufsm import PdfUfsmHistoricoProvider
from app.repositories.historicos import (
    SqlAlchemyEquivalenciaManualRepository,
    SqlAlchemyHistoricoImportacaoRepository,
)
from app.services.historicos import EquivalenciaManualService, ImportacaoHistoricoService

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_history_import_service(
    session: DatabaseSession,
    academic: AcademicProvider,
) -> ImportacaoHistoricoService:
    return ImportacaoHistoricoService(
        academic=academic,
        documents=PdfUfsmHistoricoProvider(),
        imports=SqlAlchemyHistoricoImportacaoRepository(session),
    )


ImportacaoHistoricoServiceDep = Annotated[
    ImportacaoHistoricoService, Depends(get_history_import_service)
]


def get_manual_equivalence_service(
    session: DatabaseSession,
    academic: AcademicProvider,
) -> EquivalenciaManualService:
    return EquivalenciaManualService(
        academic=academic,
        equivalences=SqlAlchemyEquivalenciaManualRepository(session),
    )


EquivalenciaManualServiceDep = Annotated[
    EquivalenciaManualService, Depends(get_manual_equivalence_service)
]
