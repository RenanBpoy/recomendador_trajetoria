from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import DatabaseSession
from app.dependencies.providers import AcademicProvider
from app.repositories.planos import SqlAlchemyPlanoSemanalRepository
from app.repositories.questionarios import SqlAlchemyQuestionarioRepository
from app.services.recomendacoes import RecomendacaoService


def get_recommendation_service(
    provider: AcademicProvider,
    session: DatabaseSession,
) -> RecomendacaoService:
    return RecomendacaoService(
        provider=provider,
        planos=SqlAlchemyPlanoSemanalRepository(session),
        questionarios=SqlAlchemyQuestionarioRepository(session),
    )


RecomendacaoServiceDep = Annotated[
    RecomendacaoService,
    Depends(get_recommendation_service),
]
