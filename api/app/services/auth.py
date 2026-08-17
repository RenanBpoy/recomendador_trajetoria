from app.core.errors import ConflictError, ResourceNotFoundError
from app.domain.entities import LoginResult, SignupCommand, SignupResult
from app.domain.ports import AuthProvider, UserRegistrationRepository


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
        return LoginResult(
            usuario=result.usuario,
            sessao=result.sessao,
            perfil=profile,
        )
