from datetime import time
from typing import Annotated

from fastapi import APIRouter, Query, Request, Response
from pydantic import BaseModel, Field, SecretStr

from app.dependencies.auth import AppSettings, CurrentAccessToken, DatabaseSession
from app.schemas.auth import LoginOut
from app.schemas.common import ApiResponse, response_meta
from app.services.ufsm_auth import UfsmAuthService, portal_account_url
from app.services.ufsm_offerings import list_offerings, list_other_courses

router = APIRouter(prefix="/autenticacao/ufsm", tags=["Autenticação"])


class UfsmCallbackRequest(BaseModel):
    code: SecretStr = Field(min_length=1, max_length=1024)
    tentativa: SecretStr = Field(min_length=43, max_length=43)


class UfsmPortalOut(BaseModel):
    url: str
    tentativa: str


class UfsmVinculoOut(BaseModel):
    id: int
    matricula: str
    curso_codigo: str
    curso_nome: str | None = None


class UfsmConfirmationOut(BaseModel):
    confirmacao: str
    nome: str
    vinculos: list[UfsmVinculoOut]


class UfsmConfirmationRequest(BaseModel):
    confirmacao: SecretStr = Field(min_length=43, max_length=43)
    vinculo_id: int = Field(gt=0, strict=True)


@router.get("/configuracao")
async def configuration(settings: AppSettings):
    data = {"habilitado": settings.ufsm_auth_enabled}
    if settings.ufsm_auth_enabled:
        data["url_portal"] = portal_account_url(settings)
    return {"data": data}


@router.post("/iniciar", response_model=ApiResponse[UfsmPortalOut])
async def start_portal(
    request: Request, response: Response, settings: AppSettings, session: DatabaseSession,
):
    response.headers["Cache-Control"] = "no-store"
    url, attempt = UfsmAuthService(settings, session).start_portal_login(request.headers.get("Origin"))
    return ApiResponse(data=UfsmPortalOut(url=url, tentativa=attempt), meta=response_meta(request))


@router.post("/callback", response_model=ApiResponse[UfsmConfirmationOut])
async def portal_callback(
    body: UfsmCallbackRequest, request: Request, response: Response, settings: AppSettings, session: DatabaseSession,
):
    response.headers["Cache-Control"] = "no-store"
    result = await UfsmAuthService(settings, session).complete_portal_login(
        body.code.get_secret_value(), body.tentativa.get_secret_value(),
    )
    return ApiResponse(data=UfsmConfirmationOut.model_validate(result), meta=response_meta(request))


@router.post("/confirmar", response_model=ApiResponse[LoginOut])
async def confirm_portal(
    body: UfsmConfirmationRequest, request: Request, response: Response, settings: AppSettings, session: DatabaseSession,
):
    response.headers["Cache-Control"] = "no-store"
    result = await UfsmAuthService(settings, session).confirm_portal_login(
        body.confirmacao.get_secret_value(), body.vinculo_id,
    )
    return ApiResponse(data=LoginOut.model_validate(result), meta=response_meta(request))


@router.post("/sair")
async def logout(token: CurrentAccessToken, settings: AppSettings, session: DatabaseSession):
    await UfsmAuthService(settings, session).logout(token)
    return {"data": {"encerrada": True}}


@router.get("/grade")
async def academic_grade(
    token: CurrentAccessToken, settings: AppSettings, session: DatabaseSession, response: Response,
):
    response.headers["Cache-Control"] = "no-store"
    return {"data": await UfsmAuthService(settings, session).grade(token)}


@router.get("/plano/cursos", description="Lista os demais cursos da UFSM sem consultar suas ofertas.")
async def plan_courses(
    token: CurrentAccessToken, settings: AppSettings, session: DatabaseSession,
):
    return {"data": await list_other_courses(
        UfsmAuthService(settings, session), token,
    )}


@router.get("/plano/ofertas", description="Consulta um único curso e filtra as turmas que coincidem com o intervalo.")
async def plan_offerings(
    token: CurrentAccessToken, settings: AppSettings, session: DatabaseSession, response: Response,
    dia_semana: Annotated[int, Query(ge=1, le=5)], hora_inicio: time, hora_fim: time,
    curso_codigo: Annotated[str | None, Query(pattern=r"^[0-9A-Za-z._-]{1,30}$")] = None,
):
    response.headers["Cache-Control"] = "no-store"
    return {"data": await list_offerings(
        UfsmAuthService(settings, session), token, curso_codigo, dia_semana, hora_inicio, hora_fim,
    )}
