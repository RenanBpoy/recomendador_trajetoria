from fastapi import APIRouter, Query, Request

from app.dependencies.auth import CurrentProfileDep
from app.dependencies.recomendacoes import RecomendacaoServiceDep
from app.schemas.common import ApiResponse, ErrorResponse, response_meta
from app.schemas.recomendacoes import ContextoSemestreOut, RecomendacaoAtualOut


router = APIRouter(prefix="/recomendacoes", tags=["Recomendações"])


@router.get(
    "/contexto",
    response_model=ApiResponse[ContextoSemestreOut],
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Calcular o semestre curricular do usuário pela matrícula",
)
async def get_recommendation_context(
    request: Request,
    profile: CurrentProfileDep,
    service: RecomendacaoServiceDep,
    ano: int | None = Query(default=None, ge=1900, le=2200),
    semestre: int | None = Query(default=None, ge=1, le=2),
) -> ApiResponse[ContextoSemestreOut]:
    context = await service.get_context(profile, ano=ano, semestre=semestre)
    return ApiResponse(
        data=ContextoSemestreOut.model_validate(context),
        meta=response_meta(request),
    )


@router.get(
    "/atual",
    response_model=ApiResponse[RecomendacaoAtualOut],
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Gerar a recomendação inicial explicável para o próximo semestre",
)
async def get_current_recommendation(
    request: Request,
    profile: CurrentProfileDep,
    service: RecomendacaoServiceDep,
    ano: int | None = Query(default=None, ge=1900, le=2200),
    semestre: int | None = Query(default=None, ge=1, le=2),
) -> ApiResponse[RecomendacaoAtualOut]:
    recommendation = await service.recommend(profile, ano=ano, semestre=semestre)
    return ApiResponse(
        data=RecomendacaoAtualOut.model_validate(recommendation),
        meta=response_meta(request),
    )
