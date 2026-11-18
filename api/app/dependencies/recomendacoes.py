from typing import Annotated

from fastapi import Depends

from app.dependencies.auth import AppSettings, CurrentAccessToken, CurrentProfileDep, DatabaseSession
from app.dependencies.providers import AcademicProvider
from app.providers.ufsm_recommendation import UfsmRecommendationProvider
from app.repositories.planos import SqlAlchemyPlanoSemanalRepository
from app.repositories.questionarios import SqlAlchemyQuestionarioRepository
from app.services.recomendacoes import RecomendacaoService
from app.services.ufsm_auth import LOCAL_PREFIX, UfsmAuthService


async def get_recommendation_service(
    provider: AcademicProvider,
    session: DatabaseSession,
    settings: AppSettings,
    access_token: CurrentAccessToken,
    profile: CurrentProfileDep,
) -> RecomendacaoService:
    if access_token.startswith(LOCAL_PREFIX):
        auth = UfsmAuthService(settings, session)
        academic_token = auth.academic_token(access_token)
        snapshot = await auth.grade(access_token)
        provider = UfsmRecommendationProvider(auth, academic_token, snapshot, profile, provider)
    return RecomendacaoService(
        provider=provider,
        planos=SqlAlchemyPlanoSemanalRepository(session),
        questionarios=SqlAlchemyQuestionarioRepository(session),
    )


RecomendacaoServiceDep = Annotated[
    RecomendacaoService,
    Depends(get_recommendation_service),
]
