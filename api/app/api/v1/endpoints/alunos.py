from datetime import time
from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.core.errors import ApplicationError
from app.dependencies.auth import CurrentProfileDep
from app.dependencies.providers import HistoricoEscolarServiceDep
from app.schemas.academic import ItemHistoricoEscolarResponse, OfertaTurmaResponse
from app.schemas.common import ApiResponse, ErrorResponse, response_meta

router = APIRouter(prefix="/alunos", tags=["Alunos"])


@router.get(
    "/{matricula}/historico",
    response_model=ApiResponse[list[ItemHistoricoEscolarResponse]],
    responses={404: {"model": ErrorResponse}},
    summary="Consultar o histórico escolar pela matrícula",
)
async def get_school_history(
    matricula: str,
    request: Request,
    service: HistoricoEscolarServiceDep,
    profile: CurrentProfileDep,
) -> ApiResponse[list[ItemHistoricoEscolarResponse]]:
    if profile.matricula != matricula:
        raise ApplicationError(
            "O histórico solicitado não pertence ao usuário logado.",
            code="historico_nao_autorizado",
            status_code=403,
        )
    history = await service.get(matricula)
    return ApiResponse(
        data=[ItemHistoricoEscolarResponse.model_validate(item) for item in history],
        meta=response_meta(request),
    )


@router.get(
    "/{matricula}/disciplinas-nao-aprovadas",
    response_model=ApiResponse[list[OfertaTurmaResponse]],
    responses={401: {"model": ErrorResponse}, 403: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Listar disciplinas disponíveis no intervalo do plano",
)
async def list_not_approved_disciplines(
    matricula: str,
    request: Request,
    service: HistoricoEscolarServiceDep,
    profile: CurrentProfileDep,
    ano: Annotated[int, Query(ge=1900, le=2200)],
    semestre: Annotated[int, Query(ge=1, le=2)],
    dia_semana: Annotated[int, Query(ge=1, le=5)],
    hora_inicio: time,
    hora_fim: time,
) -> ApiResponse[list[OfertaTurmaResponse]]:
    if profile.matricula != matricula:
        raise ApplicationError(
            "As disciplinas solicitadas não pertencem ao usuário logado.",
            code="disciplinas_nao_autorizadas",
            status_code=403,
        )
    offerings = await service.list_available_discipline_offerings(
        matricula,
        ano=ano,
        semestre=semestre,
        dia_semana=dia_semana,
        hora_inicio=hora_inicio,
        hora_fim=hora_fim,
    )
    return ApiResponse(
        data=[OfertaTurmaResponse.model_validate(item) for item in offerings],
        meta=response_meta(request),
    )
