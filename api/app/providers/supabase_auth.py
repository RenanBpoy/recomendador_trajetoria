from typing import Any
from uuid import UUID

import httpx

from app.core.errors import (
    ApplicationError,
    AuthenticationError,
    ConflictError,
    DataSourceUnavailableError,
    RateLimitError,
)
from app.domain.entities import (
    AuthSession,
    AuthUser,
    LoginResult,
    SignupCommand,
    SignupResult,
)


class SupabaseAuthProvider:
    """Adapta a API HTTP do Supabase Auth ao contrato usado pelo service."""

    def __init__(
        self,
        *,
        supabase_url: str,
        publishable_key: str,
        timeout_seconds: float = 10.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._auth_url = f"{supabase_url.rstrip('/')}/auth/v1"
        self._headers = {
            "apikey": publishable_key,
            "Content-Type": "application/json",
        }
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def signup(self, command: SignupCommand) -> SignupResult:
        payload = await self._post(
            "/signup",
            json={
                "email": command.email,
                "password": command.senha,
                "data": {
                    "nome": command.nome,
                    "matricula": command.matricula,
                    "curso_codigo": command.curso_codigo,
                    "data_nascimento": command.data_nascimento.isoformat(),
                },
            },
            operation="signup",
        )

        user_payload = payload.get("user") or payload
        user = self._user(user_payload, fallback_email=command.email)
        session = self._session(payload)
        return SignupResult(
            usuario=user,
            sessao=session,
            confirmacao_email_necessaria=session is None,
        )

    async def login(self, *, email: str, password: str) -> LoginResult:
        payload = await self._post(
            "/token",
            params={"grant_type": "password"},
            json={"email": email, "password": password},
            operation="login",
        )
        session = self._session(payload)
        if session is None:
            raise DataSourceUnavailableError(
                "O serviço de autenticação retornou uma sessão incompleta."
            )
        return LoginResult(
            usuario=self._user(payload.get("user"), fallback_email=email),
            sessao=session,
        )

    async def _post(
        self,
        path: str,
        *,
        json: dict[str, Any],
        operation: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                response = await client.post(
                    f"{self._auth_url}{path}",
                    headers=self._headers,
                    params=params,
                    json=json,
                )
        except httpx.RequestError as exc:
            raise DataSourceUnavailableError(
                "O serviço de autenticação está indisponível."
            ) from exc

        if response.is_error:
            self._raise_provider_error(response, operation=operation)

        try:
            payload = response.json()
        except ValueError as exc:
            raise DataSourceUnavailableError(
                "O serviço de autenticação retornou uma resposta inválida."
            ) from exc
        if not isinstance(payload, dict):
            raise DataSourceUnavailableError(
                "O serviço de autenticação retornou uma resposta inválida."
            )
        return payload

    @staticmethod
    def _raise_provider_error(response: httpx.Response, *, operation: str) -> None:
        try:
            body = response.json()
        except ValueError:
            body = {}
        if not isinstance(body, dict):
            body = {}

        provider_code = str(body.get("error_code") or body.get("code") or "")
        provider_message = str(body.get("msg") or body.get("message") or "")
        normalized = f"{provider_code} {provider_message}".lower()

        if response.status_code == 429:
            raise RateLimitError()
        if response.status_code >= 500:
            raise DataSourceUnavailableError(
                "O serviço de autenticação está temporariamente indisponível."
            )
        if operation == "login" and provider_code == "email_not_confirmed":
            raise AuthenticationError(
                "Confirme seu e-mail antes de entrar na sua conta."
            )
        if operation == "login" and (
            "invalid" in normalized or "credentials" in normalized
        ):
            raise AuthenticationError()
        if operation == "signup" and (
            "already" in normalized
            or "exists" in normalized
            or provider_code in {"email_exists", "user_already_exists"}
        ):
            raise ConflictError("Já existe uma conta cadastrada com este e-mail.")
        if "weak_password" in normalized or "password" in provider_code:
            raise ApplicationError(
                "A senha não atende aos requisitos do serviço de autenticação.",
                code="invalid_password",
                details={"provider_code": provider_code or None},
            )
        if operation == "login":
            raise AuthenticationError()
        raise ApplicationError(
            "Não foi possível concluir o cadastro no serviço de autenticação.",
            code="signup_rejected",
            details={"provider_code": provider_code or None},
        )

    @staticmethod
    def _user(payload: Any, *, fallback_email: str) -> AuthUser:
        if not isinstance(payload, dict) or not payload.get("id"):
            raise DataSourceUnavailableError(
                "O serviço de autenticação retornou um usuário inválido."
            )
        try:
            user_id = UUID(str(payload["id"]))
        except (TypeError, ValueError) as exc:
            raise DataSourceUnavailableError(
                "O serviço de autenticação retornou um usuário inválido."
            ) from exc
        return AuthUser(id=user_id, email=str(payload.get("email") or fallback_email))

    @staticmethod
    def _session(payload: dict[str, Any]) -> AuthSession | None:
        access_token = payload.get("access_token")
        refresh_token = payload.get("refresh_token")
        if not access_token or not refresh_token:
            return None
        return AuthSession(
            access_token=str(access_token),
            refresh_token=str(refresh_token),
            expires_in=int(payload.get("expires_in") or 0),
            token_type=str(payload.get("token_type") or "bearer"),
        )
