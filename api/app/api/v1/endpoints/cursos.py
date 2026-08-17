from typing import Annotated

from fastapi import APIRouter, Query, Request

from app.dependencies.providers import CursoServiceDep
from app.schemas.academic import CurriculoResponse, CursoResponse
from app.schemas.common import (
    ApiPageResponse,
    ApiResponse,
    ErrorResponse,
    page_meta,
    response_meta,
)

router = APIRouter(prefix="/cursos", tags=["Cursos"])


@router.get(
    "",
    response_model=ApiPageResponse[CursoResponse],
    summary="Listar cursos",
)
async def list_courses(
    request: Request,
    service: CursoServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: Annotated[str | None, Query(description="Código do último curso recebido")] = None,
) -> ApiPageResponse[CursoResponse]:
    page = await service.list(limit=limit, cursor=cursor)
    return ApiPageResponse(
        data=[CursoResponse.model_validate(item) for item in page.items],
        meta=page_meta(request, limit=limit, next_cursor=page.next_cursor),
    )


@router.get(
    "/{codigo}",
    response_model=ApiResponse[CursoResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Consultar curso pelo código oficial",
)
async def get_course(
    codigo: str,
    request: Request,
    service: CursoServiceDep,
) -> ApiResponse[CursoResponse]:
    course = await service.get(codigo)
    return ApiResponse(data=CursoResponse.model_validate(course), meta=response_meta(request))


@router.get(
    "/{codigo}/ppcs",
    response_model=ApiResponse[list[CurriculoResponse]],
    responses={404: {"model": ErrorResponse}},
    summary="Listar versões de PPC do curso",
)
async def list_course_curricula(
    codigo: str,
    request: Request,
    service: CursoServiceDep,
) -> ApiResponse[list[CurriculoResponse]]:
    curricula = await service.list_curricula(codigo)
    return ApiResponse(
        data=[CurriculoResponse.model_validate(item) for item in curricula],
        meta=response_meta(request),
    )
