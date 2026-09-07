from typing import Any
from urllib.parse import quote
from uuid import UUID, uuid4

import httpx

from app.core.errors import (
    ApplicationError,
    AuthenticationError,
    DataSourceUnavailableError,
)


class SupabaseStorageProvider:
    """Adapta o Supabase Storage ao contrato de fotos de perfil."""

    _extensions = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
    }

    def __init__(
        self,
        *,
        supabase_url: str,
        publishable_key: str,
        bucket: str = "avatares-perfil",
        signed_url_seconds: int = 3600,
        timeout_seconds: float = 15.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = supabase_url.rstrip("/")
        self._storage_url = f"{self._base_url}/storage/v1"
        self._publishable_key = publishable_key
        self._bucket = bucket
        self._signed_url_seconds = signed_url_seconds
        self._timeout_seconds = timeout_seconds
        self._transport = transport

    async def upload(
        self,
        *,
        user_id: UUID,
        access_token: str,
        content: bytes,
        content_type: str,
    ) -> str:
        extension = self._extensions[content_type]
        path = f"{user_id}/{uuid4()}{extension}"
        response = await self._request(
            "POST",
            f"/object/{self._bucket}/{quote(path, safe='/')}",
            access_token=access_token,
            content=content,
            content_type=content_type,
            extra_headers={"cache-control": "3600"},
        )
        if response.is_error:
            self._raise_storage_error(response, "enviar a foto")
        return path

    async def delete(self, *, path: str, access_token: str) -> None:
        response = await self._request(
            "DELETE",
            f"/object/{self._bucket}",
            access_token=access_token,
            json={"prefixes": [path]},
        )
        if response.status_code == 404:
            return
        if response.is_error:
            self._raise_storage_error(response, "remover a foto")

    async def delete_user_files(self, *, user_id: UUID, access_token: str) -> None:
        """Remove também versões antigas de fotos, somente da pasta do usuário."""
        previous_paths = None
        while True:
            response = await self._request(
                "POST", f"/object/list/{self._bucket}",
                access_token=access_token,
                json={"prefix": str(user_id), "limit": 100, "offset": 0},
            )
            if response.is_error:
                self._raise_storage_error(response, "listar as fotos da conta")
            try:
                files = response.json()
                if not isinstance(files, list):
                    raise ValueError()
                paths = []
                for item in files:
                    name = item.get("name", "")
                    if not item.get("id") or not name or "/" in name or name in {".", ".."}:
                        raise ValueError()
                    paths.append(f"{user_id}/{name}")
            except (ValueError, AttributeError, TypeError) as exc:
                raise DataSourceUnavailableError("Não foi possível verificar as fotos da conta.") from exc
            if not paths:
                return
            if paths == previous_paths:
                raise DataSourceUnavailableError("Não foi possível remover todas as fotos. Tente novamente.")
            previous_paths = paths
            for path in paths:
                await self.delete(path=path, access_token=access_token)

    async def create_signed_url(
        self, *, path: str, access_token: str
    ) -> str:
        response = await self._request(
            "POST",
            f"/object/sign/{self._bucket}/{quote(path, safe='/')}",
            access_token=access_token,
            json={"expiresIn": self._signed_url_seconds},
        )
        if response.is_error:
            self._raise_storage_error(response, "carregar a foto")
        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise DataSourceUnavailableError(
                "O armazenamento retornou uma resposta inválida."
            ) from exc
        signed_url = payload.get("signedURL") if isinstance(payload, dict) else None
        if not signed_url:
            raise DataSourceUnavailableError(
                "O armazenamento não retornou o endereço temporário da foto."
            )
        signed_url = str(signed_url)
        if signed_url.startswith("http://") or signed_url.startswith("https://"):
            return signed_url
        if signed_url.startswith("/storage/v1"):
            return f"{self._base_url}{signed_url}"
        return f"{self._storage_url}/{signed_url.lstrip('/')}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        access_token: str,
        content: bytes | None = None,
        content_type: str | None = None,
        json: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        headers = {
            "apikey": self._publishable_key,
            "Authorization": f"Bearer {access_token}",
            **(extra_headers or {}),
        }
        if content_type:
            headers["Content-Type"] = content_type
        elif json is not None:
            headers["Content-Type"] = "application/json"
        try:
            async with httpx.AsyncClient(
                timeout=self._timeout_seconds,
                transport=self._transport,
            ) as client:
                return await client.request(
                    method,
                    f"{self._storage_url}{path}",
                    headers=headers,
                    content=content,
                    json=json,
                )
        except httpx.RequestError as exc:
            raise DataSourceUnavailableError(
                "O armazenamento de fotos está indisponível."
            ) from exc

    @staticmethod
    def _raise_storage_error(response: httpx.Response, operation: str) -> None:
        if response.status_code in {401, 403}:
            raise AuthenticationError(
                "Sua sessão não permite acessar esta foto. Entre novamente."
            )
        if response.status_code >= 500:
            raise DataSourceUnavailableError(
                f"Não foi possível {operation}: o armazenamento está indisponível."
            )
        raise ApplicationError(
            f"Não foi possível {operation}.",
            code="avatar_storage_error",
            details={"storage_status": response.status_code},
        )
