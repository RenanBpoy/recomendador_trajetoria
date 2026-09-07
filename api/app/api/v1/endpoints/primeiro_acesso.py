from fastapi import APIRouter, Request

from app.dependencies.auth import CurrentProfileDep
from app.dependencies.primeiro_acesso import PrimeiroAcessoServiceDep
from app.schemas.common import ApiResponse, ErrorResponse, response_meta
from app.schemas.primeiro_acesso import ResetPrimeiroAcessoOut

router = APIRouter(prefix="/primeiro-acesso", tags=["Primeiro acesso"])


@router.delete(
    "/progresso",
    response_model=ApiResponse[ResetPrimeiroAcessoOut],
    responses={401: {"model": ErrorResponse}},
    summary="Reiniciar os dados do fluxo de primeiro acesso",
)
async def reset_first_access_progress(
    request: Request,
    profile: CurrentProfileDep,
    service: PrimeiroAcessoServiceDep,
) -> ApiResponse[ResetPrimeiroAcessoOut]:
    result = await service.reset(profile.id)
    return ApiResponse(
        data=ResetPrimeiroAcessoOut(
            mensagem="Dados do primeiro acesso removidos com sucesso.",
            historicos_importados_removidos=result.historicos_importados_removidos,
            equivalencias_manuais_removidas=result.equivalencias_manuais_removidas,
            questionarios_reiniciados=result.questionarios_reiniciados,
            itens_plano_removidos=result.itens_plano_removidos,
        ),
        meta=response_meta(request),
    )
