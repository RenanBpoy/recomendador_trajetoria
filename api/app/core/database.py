from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool

from app.core.config import get_settings
from app.core.errors import DataSourceUnavailableError


def normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql://"):
        return database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    if database_url.startswith("postgresql+psycopg://"):
        return database_url
    raise RuntimeError("DATABASE_URL deve usar o protocolo postgres ou postgresql.")


@lru_cache
def get_engine() -> AsyncEngine:
    settings = get_settings()
    engine_options: dict[str, object] = {
        "echo": settings.database_echo,
        "pool_pre_ping": True,
    }

    if settings.database_pool_mode == "transaction":
        engine_options.update(
            poolclass=NullPool,
            connect_args={"prepare_threshold": None},
        )
    else:
        engine_options.update(
            pool_size=settings.database_pool_size,
            max_overflow=settings.database_max_overflow,
        )

    try:
        database_url = normalize_database_url(settings.require_database_url())
    except RuntimeError as exc:
        raise DataSourceUnavailableError(str(exc)) from exc

    return create_async_engine(database_url, **engine_options)


@lru_cache
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(get_engine(), expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with get_session_factory()() as session:
        try:
            yield session
        except OperationalError as exc:
            await session.rollback()
            raise DataSourceUnavailableError() from exc
        except Exception:
            await session.rollback()
            raise


async def dispose_database() -> None:
    if get_engine.cache_info().currsize:
        await get_engine().dispose()
    get_session_factory.cache_clear()
    get_engine.cache_clear()
