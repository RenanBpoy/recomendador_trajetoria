from fastapi import APIRouter, Request

from app.dependencies.providers import CurriculoServiceDep
from app.schemas.academic import ComponenteCurricularResponse, CurriculoResponse
from app.schemas.common import ApiResponse, ErrorResponse, response_meta

router = APIRouter(prefix="/ppcs", tags=["PPCs"])


@router.get(
    "/{ppc_id}",
    response_model=ApiResponse[CurriculoResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Consultar uma versão de PPC",
)
async def get_curriculum(
    ppc_id: int,
    request: Request,
    service: CurriculoServiceDep,
) -> ApiResponse[CurriculoResponse]:
    curriculum = await service.get(ppc_id)
    return ApiResponse(
        data=CurriculoResponse.model_validate(curriculum),
        meta=response_meta(request),
    )


@router.get(
    "/{ppc_id}/componentes",
    response_model=ApiResponse[list[ComponenteCurricularResponse]],
    responses={404: {"model": ErrorResponse}},
    summary="Listar a sequência aconselhada do PPC",
)
async def list_curriculum_components(
    ppc_id: int,
    request: Request,
    service: CurriculoServiceDep,
) -> ApiResponse[list[ComponenteCurricularResponse]]:
    components = await service.list_components(ppc_id)
    return ApiResponse(
        data=[ComponenteCurricularResponse.model_validate(item) for item in components],
        meta=response_meta(request),
    )
