from fastapi import APIRouter, File, Request, Response, UploadFile, status

from app.dependencies.auth import CurrentProfileDep
from app.dependencies.historicos import (
    EquivalenciaManualServiceDep,
    ImportacaoHistoricoServiceDep,
)
from app.schemas.common import ApiResponse, ErrorResponse, response_meta
from app.schemas.historicos import (
    CandidatoEquivalenciaResponse,
    EquivalenciaManualResponse,
    ImportacaoHistoricoResponse,
    RevisarCorrespondenciaRequest,
    SalvarEquivalenciaManualRequest,
)
from app.services.historicos import MAX_PDF_SIZE

router = APIRouter(prefix="/historicos", tags=["Históricos"])


@router.post(
    "/importacoes",
    response_model=ApiResponse[ImportacaoHistoricoResponse],
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Importar um histórico escolar em PDF",
)
async def import_history(
    request: Request,
    profile: CurrentProfileDep,
    service: ImportacaoHistoricoServiceDep,
    arquivo: UploadFile = File(...),
) -> ApiResponse[ImportacaoHistoricoResponse]:
    content = await arquivo.read(MAX_PDF_SIZE + 1)
    result = await service.import_pdf(
        profile=profile,
        filename=arquivo.filename or "historico.pdf",
        content=content,
    )
    return ApiResponse(
        data=ImportacaoHistoricoResponse.model_validate(result),
        meta=response_meta(request),
    )


@router.get(
    "/importacoes/atual",
    response_model=ApiResponse[ImportacaoHistoricoResponse | None],
    responses={401: {"model": ErrorResponse}},
    summary="Consultar a importação ativa do usuário",
)
async def get_active_import(
    request: Request,
    profile: CurrentProfileDep,
    service: ImportacaoHistoricoServiceDep,
) -> ApiResponse[ImportacaoHistoricoResponse | None]:
    result = await service.get_active(profile.id)
    return ApiResponse(
        data=ImportacaoHistoricoResponse.model_validate(result) if result else None,
        meta=response_meta(request),
    )


@router.patch(
    "/correspondencias/{correspondencia_id}",
    response_model=ApiResponse[ImportacaoHistoricoResponse],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Confirmar ou rejeitar uma correspondência sugerida",
)
async def review_correspondence(
    correspondencia_id: int,
    body: RevisarCorrespondenciaRequest,
    request: Request,
    profile: CurrentProfileDep,
    service: ImportacaoHistoricoServiceDep,
) -> ApiResponse[ImportacaoHistoricoResponse]:
    result = await service.review(
        user_id=profile.id,
        correspondence_id=correspondencia_id,
        action=body.acao,
    )
    return ApiResponse(
        data=ImportacaoHistoricoResponse.model_validate(result),
        meta=response_meta(request),
    )


@router.get(
    "/equivalencias-manuais",
    response_model=ApiResponse[list[EquivalenciaManualResponse]],
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Listar equivalências escolhidas pelo usuário",
)
async def list_manual_equivalences(
    request: Request,
    profile: CurrentProfileDep,
    service: EquivalenciaManualServiceDep,
) -> ApiResponse[list[EquivalenciaManualResponse]]:
    mappings = await service.list_mappings(profile=profile)
    return ApiResponse(
        data=[EquivalenciaManualResponse.model_validate(item) for item in mappings],
        meta=response_meta(request),
    )


@router.get(
    "/componentes/{componente_id}/candidatos-equivalencia",
    response_model=ApiResponse[list[CandidatoEquivalenciaResponse]],
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Listar disciplinas não mapeadas que podem preencher um componente",
)
async def list_equivalence_candidates(
    componente_id: int,
    request: Request,
    profile: CurrentProfileDep,
    service: EquivalenciaManualServiceDep,
) -> ApiResponse[list[CandidatoEquivalenciaResponse]]:
    candidates = await service.list_candidates(
        profile=profile,
        component_id=componente_id,
    )
    return ApiResponse(
        data=[CandidatoEquivalenciaResponse.model_validate(item) for item in candidates],
        meta=response_meta(request),
    )


@router.put(
    "/componentes/{componente_id}/vagas/{vaga_ordem}/equivalencia",
    response_model=ApiResponse[EquivalenciaManualResponse],
    responses={
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
    },
    summary="Salvar a disciplina escolhida para uma vaga da grade",
)
async def save_manual_equivalence(
    componente_id: int,
    vaga_ordem: int,
    body: SalvarEquivalenciaManualRequest,
    request: Request,
    profile: CurrentProfileDep,
    service: EquivalenciaManualServiceDep,
) -> ApiResponse[EquivalenciaManualResponse]:
    mapping = await service.save(
        profile=profile,
        component_id=componente_id,
        slot_order=vaga_ordem,
        history_item_id=body.historico_item_id,
    )
    return ApiResponse(
        data=EquivalenciaManualResponse.model_validate(mapping),
        meta=response_meta(request),
    )


@router.delete(
    "/componentes/{componente_id}/vagas/{vaga_ordem}/equivalencia",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Remover uma equivalência escolhida pelo usuário",
)
async def remove_manual_equivalence(
    componente_id: int,
    vaga_ordem: int,
    profile: CurrentProfileDep,
    service: EquivalenciaManualServiceDep,
) -> Response:
    await service.remove(
        profile=profile,
        component_id=componente_id,
        slot_order=vaga_ordem,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
