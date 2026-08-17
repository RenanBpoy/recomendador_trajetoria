from fastapi import APIRouter, Request

from app.dependencies.providers import HistoricoEscolarServiceDep
from app.schemas.academic import ItemHistoricoEscolarResponse
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
) -> ApiResponse[list[ItemHistoricoEscolarResponse]]:
    history = await service.get(matricula)
    return ApiResponse(
        data=[ItemHistoricoEscolarResponse.model_validate(item) for item in history],
        meta=response_meta(request),
    )
