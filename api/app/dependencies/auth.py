from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.database import get_db_session
from app.domain.ports import AuthProvider, AvatarStorageProvider
from app.domain.entities import AuthUser, UserProfile
from app.core.errors import AuthenticationError, ResourceNotFoundError
from app.providers.supabase_auth import SupabaseAuthProvider
from app.providers.supabase_storage import SupabaseStorageProvider
from app.repositories.users import SqlAlchemyUserRegistrationRepository
from app.services.auth import AuthService, PerfilService

DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]
AppSettings = Annotated[Settings, Depends(get_settings)]


def get_auth_provider(settings: AppSettings) -> AuthProvider:
    return SupabaseAuthProvider(
        supabase_url=settings.require_supabase_url(),
        publishable_key=settings.require_supabase_publishable_key(),
    )


AuthProviderDep = Annotated[AuthProvider, Depends(get_auth_provider)]
_bearer = HTTPBearer(auto_error=False)


async def get_current_access_token(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise AuthenticationError("É necessário entrar na conta para acessar este recurso.")
    return credentials.credentials


CurrentAccessToken = Annotated[str, Depends(get_current_access_token)]


async def get_current_user(
    access_token: CurrentAccessToken,
    provider: AuthProviderDep,
) -> AuthUser:
    return await provider.get_user(access_token)


CurrentAuthUser = Annotated[AuthUser, Depends(get_current_user)]


async def get_current_profile(
    user: CurrentAuthUser,
    session: DatabaseSession,
) -> UserProfile:
    profile = await SqlAlchemyUserRegistrationRepository(session).get_profile(user.id)
    if profile is None:
        raise ResourceNotFoundError("Perfil do usuário", user.id)
    return profile


CurrentProfileDep = Annotated[UserProfile, Depends(get_current_profile)]


def get_auth_service(
    session: DatabaseSession,
    provider: AuthProviderDep,
) -> AuthService:
    return AuthService(
        users=SqlAlchemyUserRegistrationRepository(session),
        auth=provider,
    )


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


def get_avatar_storage_provider(settings: AppSettings) -> AvatarStorageProvider:
    return SupabaseStorageProvider(
        supabase_url=settings.require_supabase_url(),
        publishable_key=settings.require_supabase_publishable_key(),
    )


AvatarStorageProviderDep = Annotated[
    AvatarStorageProvider, Depends(get_avatar_storage_provider)
]


def get_profile_service(
    session: DatabaseSession,
    auth_provider: AuthProviderDep,
    avatar_provider: AvatarStorageProviderDep,
) -> PerfilService:
    return PerfilService(
        users=SqlAlchemyUserRegistrationRepository(session),
        auth=auth_provider,
        avatars=avatar_provider,
    )


PerfilServiceDep = Annotated[PerfilService, Depends(get_profile_service)]
