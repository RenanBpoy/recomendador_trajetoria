from fastapi import APIRouter, Request

from app.dependencies.auth import CurrentProfileDep
from app.dependencies.planos import PlanoSemanalServiceDep
from app.domain.entities import PlanoSemanaItemInput
from app.schemas.common import ApiResponse, ErrorResponse, response_meta
from app.schemas.planos import (
    PlanoSemanaItemOut,
    PlanoSemanaReplaceRequest,
)

router = APIRouter(prefix="/plano-semanal", tags=["Plano semanal"])


@router.get(
    "",
    response_model=ApiResponse[list[PlanoSemanaItemOut]],
    responses={401: {"model": ErrorResponse}},
    summary="Consultar o plano semanal do usuário",
)
async def get_weekly_plan(
    request: Request,
    profile: CurrentProfileDep,
    service: PlanoSemanalServiceDep,
) -> ApiResponse[list[PlanoSemanaItemOut]]:
    items = await service.get(profile.id)
    return ApiResponse(
        data=[PlanoSemanaItemOut.model_validate(item) for item in items],
        meta=response_meta(request),
    )


@router.put(
    "",
    response_model=ApiResponse[list[PlanoSemanaItemOut]],
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Substituir e salvar o plano semanal do usuário",
)
async def replace_weekly_plan(
    body: PlanoSemanaReplaceRequest,
    request: Request,
    profile: CurrentProfileDep,
    service: PlanoSemanalServiceDep,
) -> ApiResponse[list[PlanoSemanaItemOut]]:
    items = tuple(
        PlanoSemanaItemInput(
            tipo_atividade=item.tipo_atividade,
            titulo=item.titulo,
            dia_semana=item.dia_semana,
            hora_inicio=item.hora_inicio,
            hora_fim=item.hora_fim,
            observacoes=item.observacoes,
        )
        for item in body.itens
    )
    saved = await service.replace(user_id=profile.id, items=items)
    return ApiResponse(
        data=[PlanoSemanaItemOut.model_validate(item) for item in saved],
        meta=response_meta(request),
    )
