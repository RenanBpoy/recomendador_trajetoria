from fastapi import APIRouter, File, Request, UploadFile, status

from app.dependencies.auth import CurrentAccessToken, CurrentProfileDep, PerfilServiceDep
from app.schemas.auth import (
    EmailUpdateOut,
    OperationMessageOut,
    SelectCurriculumRequest,
    UpdateEmailRequest,
    UpdatePasswordRequest,
    UpdatePersonalDataRequest,
    UserProfileOut,
)
from app.schemas.common import ApiResponse, ErrorResponse, response_meta

router = APIRouter(prefix="/perfil", tags=["Perfil"])


@router.get(
    "",
    response_model=ApiResponse[UserProfileOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Consultar o perfil do usuário logado",
)
async def get_profile(
    request: Request,
    profile: CurrentProfileDep,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
) -> ApiResponse[UserProfileOut]:
    profile = await service.with_avatar_url(
        profile=profile,
        access_token=access_token,
    )
    return ApiResponse(
        data=UserProfileOut.model_validate(profile),
        meta=response_meta(request),
    )


@router.put(
    "/ppc",
    response_model=ApiResponse[UserProfileOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Salvar o PPC utilizado pelo estudante",
)
async def select_curriculum(
    body: SelectCurriculumRequest,
    request: Request,
    profile: CurrentProfileDep,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
) -> ApiResponse[UserProfileOut]:
    updated = await service.select_curriculum(user_id=profile.id, ppc_id=body.ppc_id)
    updated = await service.with_avatar_url(
        profile=updated,
        access_token=access_token,
    )
    return ApiResponse(
        data=UserProfileOut.model_validate(updated),
        meta=response_meta(request),
    )


@router.patch(
    "/dados-pessoais",
    response_model=ApiResponse[UserProfileOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Atualizar nome e data de nascimento",
)
async def update_personal_data(
    body: UpdatePersonalDataRequest,
    request: Request,
    profile: CurrentProfileDep,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
) -> ApiResponse[UserProfileOut]:
    updated = await service.update_personal_data(
        user_id=profile.id,
        nome=body.nome,
        data_nascimento=body.data_nascimento,
    )
    updated = await service.with_avatar_url(
        profile=updated,
        access_token=access_token,
    )
    return ApiResponse(
        data=UserProfileOut.model_validate(updated),
        meta=response_meta(request),
    )


@router.put(
    "/email",
    response_model=ApiResponse[EmailUpdateOut],
    responses={401: {"model": ErrorResponse}, 409: {"model": ErrorResponse}},
    summary="Solicitar a alteração do e-mail da conta",
)
async def update_email(
    body: UpdateEmailRequest,
    request: Request,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
) -> ApiResponse[EmailUpdateOut]:
    user = await service.update_email(
        access_token=access_token,
        email=body.email,
    )
    return ApiResponse(
        data=EmailUpdateOut(
            email_solicitado=body.email,
            confirmacao_necessaria=user.email.lower() != body.email,
        ),
        meta=response_meta(request),
    )


@router.put(
    "/senha",
    response_model=ApiResponse[OperationMessageOut],
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Alterar a senha da conta",
)
async def update_password(
    body: UpdatePasswordRequest,
    request: Request,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
) -> ApiResponse[OperationMessageOut]:
    await service.update_password(
        access_token=access_token,
        password=body.senha,
    )
    return ApiResponse(
        data=OperationMessageOut(mensagem="Senha atualizada com sucesso."),
        meta=response_meta(request),
    )


@router.post(
    "/avatar",
    response_model=ApiResponse[UserProfileOut],
    status_code=status.HTTP_201_CREATED,
    responses={401: {"model": ErrorResponse}, 422: {"model": ErrorResponse}},
    summary="Enviar ou substituir a foto do perfil",
)
async def upload_avatar(
    request: Request,
    profile: CurrentProfileDep,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
    arquivo: UploadFile = File(...),
) -> ApiResponse[UserProfileOut]:
    content = await arquivo.read(5 * 1024 * 1024 + 1)
    updated = await service.upload_avatar(
        profile=profile,
        access_token=access_token,
        content=content,
        content_type=arquivo.content_type or "",
    )
    return ApiResponse(
        data=UserProfileOut.model_validate(updated),
        meta=response_meta(request),
    )


@router.delete(
    "/avatar",
    response_model=ApiResponse[UserProfileOut],
    responses={401: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
    summary="Remover a foto do perfil",
)
async def delete_avatar(
    request: Request,
    profile: CurrentProfileDep,
    access_token: CurrentAccessToken,
    service: PerfilServiceDep,
) -> ApiResponse[UserProfileOut]:
    updated = await service.delete_avatar(
        profile=profile,
        access_token=access_token,
    )
    return ApiResponse(
        data=UserProfileOut.model_validate(updated),
        meta=response_meta(request),
    )
