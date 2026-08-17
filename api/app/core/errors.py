import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class ApplicationError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: str = "application_error",
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Any = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details


class ResourceNotFoundError(ApplicationError):
    def __init__(self, resource: str, identifier: str | int) -> None:
        super().__init__(
            f"{resource} não encontrado(a): {identifier}",
            code="resource_not_found",
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": str(identifier)},
        )


class DataSourceUnavailableError(ApplicationError):
    def __init__(self, message: str = "A fonte de dados acadêmicos está indisponível.") -> None:
        super().__init__(
            message,
            code="data_source_unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        )


class AuthenticationError(ApplicationError):
    def __init__(self, message: str = "E-mail ou senha inválidos.") -> None:
        super().__init__(
            message,
            code="authentication_failed",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )


class ConflictError(ApplicationError):
    def __init__(self, message: str, *, details: Any = None) -> None:
        super().__init__(
            message,
            code="resource_conflict",
            status_code=status.HTTP_409_CONFLICT,
            details=details,
        )


class RateLimitError(ApplicationError):
    def __init__(self, message: str = "Muitas tentativas. Tente novamente mais tarde.") -> None:
        super().__init__(
            message,
            code="rate_limit_exceeded",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        )


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _error_payload(request: Request, code: str, message: str, details: Any = None) -> dict:
    return {
        "error": {"code": code, "message": message, "details": details},
        "meta": {"request_id": _request_id(request)},
    }


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(ApplicationError)
    async def handle_application_error(request: Request, exc: ApplicationError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=_error_payload(request, exc.code, exc.message, exc.details),
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            content=_error_payload(
                request,
                "validation_error",
                "Parâmetros inválidos.",
                jsonable_encoder(exc.errors()),
            ),
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Erro inesperado na API", exc_info=exc)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=_error_payload(request, "internal_error", "Ocorreu um erro interno inesperado."),
        )
