from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.dependencies.providers import DisciplinaServiceDep
from app.schemas.academic import DisciplinaResponse
from app.schemas.common import (
    ApiPageResponse,
    ApiResponse,
    ErrorResponse,
    page_meta,
    response_meta,
)

router = APIRouter(prefix="/disciplinas", tags=["Disciplinas"])


@router.get(
    "",
    response_model=ApiPageResponse[DisciplinaResponse],
    summary="Listar disciplinas",
)
async def list_disciplines(
    request: Request,
    service: DisciplinaServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[
        str | None, Query(description="Código da última disciplina recebida")
    ] = None,
) -> ApiPageResponse[DisciplinaResponse]:
    page = await service.list(limit=limit, cursor=cursor)
    return ApiPageResponse(
        data=[DisciplinaResponse.model_validate(item) for item in page.items],
        meta=page_meta(request, limit=limit, next_cursor=page.next_cursor),
    )


@router.get(
    "/{codigo}",
    response_model=ApiResponse[DisciplinaResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Consultar disciplina pelo código oficial",
)
async def get_discipline(
    codigo: str,
    request: Request,
    service: DisciplinaServiceDep,
) -> ApiResponse[DisciplinaResponse]:
    discipline = await service.get(codigo)
    return ApiResponse(
        data=DisciplinaResponse.model_validate(discipline),
        meta=response_meta(request),
    )
