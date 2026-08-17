from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import AlunoModel, CursoModel, UsuarioModel
from app.domain.entities import UserProfile


class SqlAlchemyUserRegistrationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def student_exists(self, matricula: str) -> bool:
        statement = select(AlunoModel.matricula).where(
            AlunoModel.matricula == matricula
        )
        return (await self._session.scalar(statement)) is not None

    async def course_exists(self, codigo: str) -> bool:
        statement = select(CursoModel.codigo).where(CursoModel.codigo == codigo)
        return (await self._session.scalar(statement)) is not None

    async def registration_in_use(self, matricula: str) -> bool:
        statement = select(UsuarioModel.matricula).where(UsuarioModel.matricula == matricula)
        return (await self._session.scalar(statement)) is not None

    async def get_profile(self, user_id: UUID) -> UserProfile | None:
        model = await self._session.get(UsuarioModel, user_id)
        if model is None:
            return None
        return UserProfile(
            id=model.id,
            matricula=model.matricula,
            curso_codigo=model.curso_codigo,
            nome=model.nome,
        )
