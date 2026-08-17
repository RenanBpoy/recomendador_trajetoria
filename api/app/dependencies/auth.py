from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.domain.ports import AuthProvider
from app.providers.supabase_auth import SupabaseAuthProvider
from app.repositories.users import SqlAlchemyUserRegistrationRepository
from app.services.auth import AuthService

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_auth_provider(settings: AppSettings) -> AuthProvider:
    return SupabaseAuthProvider(
        supabase_url=settings.require_supabase_url(),
        publishable_key=settings.require_supabase_publishable_key(),
    )


AuthProviderDep = Annotated[AuthProvider, Depends(get_auth_provider)]


def get_auth_service(
    session: DatabaseSession,
    provider: AuthProviderDep,
) -> AuthService:
    return AuthService(
        users=SqlAlchemyUserRegistrationRepository(session),
        auth=provider,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
