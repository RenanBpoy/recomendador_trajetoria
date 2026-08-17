from fastapi import APIRouter, Request, status

from app.dependencies.auth import AuthServiceDep
from app.domain.entities import SignupCommand
from app.schemas.auth import LoginOut, LoginRequest, SignupOut, SignupRequest
from app.schemas.common import ApiResponse, ErrorResponse, response_meta

router = APIRouter(prefix="/autenticacao", tags=["Autenticação"])


@router.post(
    "/cadastro",
    response_model=ApiResponse[SignupOut],
    status_code=status.HTTP_201_CREATED,
    responses={
        404: {"model": ErrorResponse},
        409: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Cadastrar uma conta de estudante",
)
async def signup(
    body: SignupRequest,
    request: Request,
    service: AuthServiceDep,
) -> ApiResponse[SignupOut]:
    result = await service.signup(
        SignupCommand(
            nome=body.nome,
            matricula=body.matricula,
            email=body.email,
            data_nascimento=body.data_nascimento,
            curso_codigo=body.curso_codigo,
            senha=body.senha,
        )
    )
    return ApiResponse(data=SignupOut.model_validate(result), meta=response_meta(request))


@router.post(
    "/login",
    response_model=ApiResponse[LoginOut],
    responses={
        401: {"model": ErrorResponse},
        422: {"model": ErrorResponse},
        429: {"model": ErrorResponse},
        503: {"model": ErrorResponse},
    },
    summary="Entrar com e-mail e senha",
)
async def login(
    body: LoginRequest,
    request: Request,
    service: AuthServiceDep,
) -> ApiResponse[LoginOut]:
    result = await service.login(email=body.email, password=body.senha)
    return ApiResponse(data=LoginOut.model_validate(result), meta=response_meta(request))
