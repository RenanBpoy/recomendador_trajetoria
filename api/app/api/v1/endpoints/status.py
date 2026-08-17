from fastapi import APIRouter, Request

from app.core.config import get_settings
from app.schemas.academic import StatusResponse
from app.schemas.common import ApiResponse, response_meta

router = APIRouter(tags=["Infraestrutura"])


@router.get(
    "/status",
    response_model=ApiResponse[StatusResponse],
    summary="Verificar se a API está ativa",
)
async def health(request: Request) -> ApiResponse[StatusResponse]:
    return ApiResponse(
        data=StatusResponse(status="ok", service=get_settings().app_name),
        meta=response_meta(request),
    )
