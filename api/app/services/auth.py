import logging
from dataclasses import replace
from datetime import date

from app.core.errors import ApplicationError, ConflictError, ResourceNotFoundError
from uuid import UUID

from app.domain.entities import AuthUser, LoginResult, SignupCommand, SignupResult, UserProfile
from app.domain.ports import AuthProvider, AvatarStorageProvider, UserRegistrationRepository

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(
        self,
        users: UserRegistrationRepository,
        auth: AuthProvider,
    ) -> None:
        self._users = users
        self._auth = auth

    async def signup(self, command: SignupCommand) -> SignupResult:
        if not await self._users.student_exists(command.matricula):
            raise ResourceNotFoundError("Aluno", command.matricula)
        if not await self._users.course_exists(command.curso_codigo):
            raise ResourceNotFoundError("Curso", command.curso_codigo)
        if await self._users.registration_in_use(command.matricula):
            raise ConflictError(
                "Já existe uma conta vinculada a esta matrícula.",
                details={"matricula": command.matricula},
            )
        result = await self._auth.signup(command)
        if result.sessao is None:
            return result

        profile = await self._users.get_profile(result.usuario.id)
        if profile is None:
            raise ResourceNotFoundError("Perfil do usuário", result.usuario.id)
        return SignupResult(
            usuario=result.usuario,
            sessao=result.sessao,
            confirmacao_email_necessaria=result.confirmacao_email_necessaria,
            perfil=profile,
        )

    async def login(self, *, email: str, password: str) -> LoginResult:
        result = await self._auth.login(email=email, password=password)
        profile = await self._users.get_profile(result.usuario.id)
        if profile is None:
            raise ResourceNotFoundError("Perfil do usuário", result.usuario.id)

        profile = await self._ensure_default_curriculum(profile)
        return LoginResult(
            usuario=result.usuario,
            sessao=result.sessao,
            perfil=profile,
        )

    async def _ensure_default_curriculum(self, profile: UserProfile) -> UserProfile:
        """Seleciona o PPC de ingresso no primeiro login que ainda não possui PPC."""
        if profile.ppc_id is not None:
            return profile

        ano_ppc = self._infer_default_curriculum_year(
            curso_codigo=profile.curso_codigo,
            matricula=profile.matricula,
        )
        if ano_ppc is None:
            return profile

        updated = await self._users.select_curriculum_by_year(
            user_id=profile.id,
            ano_versao=ano_ppc,
        )
        if updated is None:
            raise ResourceNotFoundError(
                "PPC padrão do curso",
                f"{profile.curso_codigo}/{ano_ppc}",
            )
        return updated

    @staticmethod
    def _infer_default_curriculum_year(
        *, curso_codigo: str, matricula: str
    ) -> int | None:
        """Os cinco primeiros dígitos representam ano e semestre de ingresso."""
        ingresso = matricula[:5]
        if len(ingresso) != 5 or not ingresso.isdigit():
            return None

        ano_semestre = int(ingresso)
        if curso_codigo == "314":
            return 2026 if ano_semestre >= 20252 else 2009
        if curso_codigo == "307":
            if ano_semestre <= 20232:
                return 2010
            if ano_semestre >= 20241:
                return 2024
        return None


class PerfilService:
    _allowed_avatar_types = {"image/jpeg", "image/png", "image/webp"}
    _max_avatar_bytes = 5 * 1024 * 1024

    def __init__(
        self,
        users: UserRegistrationRepository,
        auth: AuthProvider,
        avatars: AvatarStorageProvider,
    ) -> None:
        self._users = users
        self._auth = auth
        self._avatars = avatars

    async def with_avatar_url(
        self, *, profile: UserProfile, access_token: str
    ) -> UserProfile:
        if not profile.avatar_path:
            return profile
        signed_url = await self._avatars.create_signed_url(
            path=profile.avatar_path,
            access_token=access_token,
        )
        return replace(profile, avatar_url=signed_url)

    async def select_curriculum(self, *, user_id: UUID, ppc_id: int) -> UserProfile:
        profile = await self._users.select_curriculum(user_id=user_id, ppc_id=ppc_id)
        if profile is None:
            raise ResourceNotFoundError("PPC compatível com o curso do usuário", ppc_id)
        return profile

    async def update_personal_data(
        self, *, user_id: UUID, nome: str, data_nascimento: date
    ) -> UserProfile:
        profile = await self._users.update_personal_data(
            user_id=user_id,
            nome=nome,
            data_nascimento=data_nascimento,
        )
        if profile is None:
            raise ResourceNotFoundError("Perfil do usuário", user_id)
        return profile

    async def update_email(
        self, *, access_token: str, email: str
    ) -> AuthUser:
        return await self._auth.update_email(
            access_token=access_token,
            email=email,
        )

    async def update_password(self, *, access_token: str, password: str) -> None:
        await self._auth.update_password(
            access_token=access_token,
            password=password,
        )

    async def upload_avatar(
        self,
        *,
        profile: UserProfile,
        access_token: str,
        content: bytes,
        content_type: str,
    ) -> UserProfile:
        normalized_type = content_type.lower().split(";", 1)[0].strip()
        if normalized_type not in self._allowed_avatar_types:
            raise ApplicationError(
                "Use uma imagem JPG, PNG ou WebP.",
                code="invalid_avatar_type",
            )
        if not content:
            raise ApplicationError(
                "A imagem enviada está vazia.",
                code="empty_avatar",
            )
        if len(content) > self._max_avatar_bytes:
            raise ApplicationError(
                "A foto deve ter no máximo 5 MB.",
                code="avatar_too_large",
            )

        new_path = await self._avatars.upload(
            user_id=profile.id,
            access_token=access_token,
            content=content,
            content_type=normalized_type,
        )
        try:
            updated = await self._users.update_avatar(
                user_id=profile.id,
                avatar_path=new_path,
            )
        except Exception:
            try:
                await self._avatars.delete(path=new_path, access_token=access_token)
            except ApplicationError:
                logger.warning("Não foi possível limpar o avatar após falha no banco.")
            raise
        if updated is None:
            await self._avatars.delete(path=new_path, access_token=access_token)
            raise ResourceNotFoundError("Perfil do usuário", profile.id)

        if profile.avatar_path and profile.avatar_path != new_path:
            try:
                await self._avatars.delete(
                    path=profile.avatar_path,
                    access_token=access_token,
                )
            except ApplicationError:
                logger.warning("Avatar antigo não pôde ser removido do Storage.")
        return await self.with_avatar_url(profile=updated, access_token=access_token)

    async def delete_avatar(
        self, *, profile: UserProfile, access_token: str
    ) -> UserProfile:
        if profile.avatar_path:
            await self._avatars.delete(
                path=profile.avatar_path,
                access_token=access_token,
            )
        updated = await self._users.update_avatar(
            user_id=profile.id,
            avatar_path=None,
        )
        if updated is None:
            raise ResourceNotFoundError("Perfil do usuário", profile.id)
        return updated
