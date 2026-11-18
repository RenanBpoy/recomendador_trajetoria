from functools import lru_cache
from typing import Literal
from urllib.parse import urlsplit

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "API do Recomendador de Trajetória"
    api_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:5173"
    frontend_url: str = "https://recomendador-trajetoria.vercel.app"

    database_url: SecretStr | None = None
    database_pool_mode: Literal["direct", "transaction"] = "transaction"
    database_pool_size: int = 5
    database_max_overflow: int = 5
    database_echo: bool = False

    supabase_url: str | None = None
    supabase_publishable_key: SecretStr | None = None
    ufsm_auth_enabled: bool = False
    ufsm_client_id: str = "ext-trajetoria-academica"
    ufsm_client_secret: SecretStr | None = None
    ufsm_portal_login_url: str = "https://sistemas-homolog.dti.ufsm.br/autenticacao/login"
    ufsm_redirect_uri: str = "http://localhost:5173/auth/callback"
    ufsm_auth_url: str = "https://api.sistemas-homolog.dti.ufsm.br/autenticacao"
    ufsm_academic_url: str = "https://api.sistemas-homolog.dti.ufsm.br/provedor-trajetoria-academica"
    ufsm_recommendation_extra_courses: str = "307,312,314"

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    def email_confirmation_url(self, origin: str | None) -> str:
        frontend = self.frontend_url.rstrip("/")
        parsed = urlsplit(frontend)
        frontend_origin = f"{parsed.scheme}://{parsed.netloc}"
        allowed = {value.rstrip("/") for value in self.allowed_origins}
        allowed.add(frontend_origin)
        return f"{origin if origin in allowed else frontend_origin}/login"

    def require_database_url(self) -> str:
        if self.database_url is None:
            raise RuntimeError(
                "DATABASE_URL não configurada. Copie .env.example para .env e informe a conexão PostgreSQL."
            )
        return self.database_url.get_secret_value()

    def require_supabase_url(self) -> str:
        if not self.supabase_url:
            raise RuntimeError(
                "SUPABASE_URL não configurada. Informe a URL do projeto no arquivo .env."
            )
        return self.supabase_url.rstrip("/")

    def require_supabase_publishable_key(self) -> str:
        if self.supabase_publishable_key is None:
            raise RuntimeError(
                "SUPABASE_PUBLISHABLE_KEY não configurada. Informe a chave pública no arquivo .env."
            )
        return self.supabase_publishable_key.get_secret_value()


@lru_cache
def get_settings() -> Settings:
    return Settings()
