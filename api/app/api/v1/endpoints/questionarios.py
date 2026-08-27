from fastapi import APIRouter, Request

from app.dependencies.auth import CurrentProfileDep
from app.dependencies.questionarios import QuestionarioServiceDep
from app.schemas.common import ApiResponse, ErrorResponse, response_meta
from app.schemas.questionarios import (
    QuestionarioAtualOut,
    QuestionarioRespostaRequest,
)

router = APIRouter(prefix="/questionarios", tags=["Questionários"])


@router.get(
    "/atual",
    response_model=ApiResponse[QuestionarioAtualOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Consultar o questionário atual e as respostas do usuário",
)
async def get_current_questionnaire(
    request: Request,
    profile: CurrentProfileDep,
    service: QuestionarioServiceDep,
) -> ApiResponse[QuestionarioAtualOut]:
    questionario = await service.get_current(profile.id)
    return ApiResponse(
        data=QuestionarioAtualOut.model_validate(questionario),
        meta=response_meta(request),
    )


@router.put(
    "/atual/respostas/{pergunta_id}",
    response_model=ApiResponse[QuestionarioAtualOut],
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
    },
    summary="Salvar uma resposta do questionário atual",
)
async def save_questionnaire_answer(
    pergunta_id: int,
    body: QuestionarioRespostaRequest,
    request: Request,
    profile: CurrentProfileDep,
    service: QuestionarioServiceDep,
) -> ApiResponse[QuestionarioAtualOut]:
    questionario = await service.save_answer(
        user_id=profile.id,
        pergunta_id=pergunta_id,
        valor=body.valor,
    )
    return ApiResponse(
        data=QuestionarioAtualOut.model_validate(questionario),
        meta=response_meta(request),
    )


@router.post(
    "/atual/concluir",
    response_model=ApiResponse[QuestionarioAtualOut],
    responses={400: {"model": ErrorResponse}, 401: {"model": ErrorResponse}},
    summary="Concluir o questionário atual",
)
async def complete_current_questionnaire(
    request: Request,
    profile: CurrentProfileDep,
    service: QuestionarioServiceDep,
) -> ApiResponse[QuestionarioAtualOut]:
    questionario = await service.complete(profile.id)
    return ApiResponse(
        data=QuestionarioAtualOut.model_validate(questionario),
        meta=response_meta(request),
    )
