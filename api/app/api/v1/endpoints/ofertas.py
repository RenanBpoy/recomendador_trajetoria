from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Request

from app.dependencies.providers import OfertaTurmaServiceDep
from app.schemas.academic import OfertaTurmaResponse, PeriodoAcademicoResponse
from app.schemas.common import (
    ApiPageResponse,
    ApiResponse,
    ErrorResponse,
    page_meta,
    response_meta,
)

router = APIRouter(tags=["Ofertas de turma"])


@router.get(
    "/ofertas-turma",
    response_model=ApiPageResponse[OfertaTurmaResponse],
    summary="Listar ofertas de turma registradas nos diários",
)
async def list_class_offerings(
    request: Request,
    service: OfertaTurmaServiceDep,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    cursor: UUID | None = None,
    curso_codigo: str | None = None,
    disciplina_codigo: str | None = None,
    ano: Annotated[int | None, Query(ge=1900, le=2200)] = None,
    semestre: Annotated[int | None, Query(ge=1, le=2)] = None,
) -> ApiPageResponse[OfertaTurmaResponse]:
    page = await service.list(
        limit=limit,
        cursor=cursor,
        curso_codigo=curso_codigo,
        disciplina_codigo=disciplina_codigo,
        ano=ano,
        semestre=semestre,
    )
    return ApiPageResponse(
        data=[OfertaTurmaResponse.model_validate(item) for item in page.items],
        meta=page_meta(request, limit=limit, next_cursor=page.next_cursor),
    )


@router.get(
    "/ofertas-turma/{oferta_id}",
    response_model=ApiResponse[OfertaTurmaResponse],
    responses={404: {"model": ErrorResponse}},
    summary="Consultar uma oferta de turma",
)
async def get_class_offering(
    oferta_id: UUID,
    request: Request,
    service: OfertaTurmaServiceDep,
) -> ApiResponse[OfertaTurmaResponse]:
    offering = await service.get(oferta_id)
    return ApiResponse(
        data=OfertaTurmaResponse.model_validate(offering),
        meta=response_meta(request),
    )


@router.get(
    "/periodos-letivos",
    response_model=ApiResponse[list[PeriodoAcademicoResponse]],
    summary="Listar anos e semestres presentes nas ofertas",
)
async def list_academic_periods(
    request: Request,
    service: OfertaTurmaServiceDep,
) -> ApiResponse[list[PeriodoAcademicoResponse]]:
    periods = await service.list_periods()
    return ApiResponse(
        data=[PeriodoAcademicoResponse.model_validate(item) for item in periods],
        meta=response_meta(request),
    )
