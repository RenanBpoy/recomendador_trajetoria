from functools import lru_cache
from typing import Literal

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

    database_url: SecretStr | None = None
    database_pool_mode: Literal["direct", "transaction"] = "transaction"
    database_pool_size: int = 5
    database_max_overflow: int = 5
    database_echo: bool = False

    supabase_url: str | None = None
    supabase_publishable_key: SecretStr | None = None

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

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
