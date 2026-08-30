from datetime import date
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.academic import (
    AlunoModel,
    CurriculoModel,
    CursoModel,
    HistoricoImportacaoModel,
    UsuarioModel,
)
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
        return self._profile(model)

    async def select_curriculum(
        self, *, user_id: UUID, ppc_id: int
    ) -> UserProfile | None:
        model = await self._session.get(UsuarioModel, user_id)
        if model is None:
            return None

        statement = select(CurriculoModel.id).where(
            CurriculoModel.id == ppc_id,
            CurriculoModel.curso_codigo == model.curso_codigo,
        )
        if await self._session.scalar(statement) is None:
            return None

        return await self._save_curriculum_selection(model=model, ppc_id=ppc_id)

    async def select_curriculum_by_year(
        self, *, user_id: UUID, ano_versao: int
    ) -> UserProfile | None:
        model = await self._session.get(UsuarioModel, user_id)
        if model is None:
            return None

        statement = select(CurriculoModel.id).where(
            CurriculoModel.curso_codigo == model.curso_codigo,
            CurriculoModel.ano_versao == ano_versao,
        )
        ppc_id = await self._session.scalar(statement)
        if ppc_id is None:
            return None

        return await self._save_curriculum_selection(model=model, ppc_id=ppc_id)

    async def _save_curriculum_selection(
        self, *, model: UsuarioModel, ppc_id: int
    ) -> UserProfile:
        model.ppc_id = ppc_id
        await self._session.execute(
            update(HistoricoImportacaoModel)
            .where(
                HistoricoImportacaoModel.usuario_id == model.id,
                HistoricoImportacaoModel.ativa.is_(True),
            )
            .values(ppc_referencia_id=ppc_id)
        )
        await self._session.commit()
        await self._session.refresh(model)
        return self._profile(model)

    async def update_personal_data(
        self, *, user_id: UUID, nome: str, data_nascimento: date
    ) -> UserProfile | None:
        model = await self._session.get(UsuarioModel, user_id)
        if model is None:
            return None
        model.nome = nome
        model.data_nascimento = data_nascimento
        await self._session.commit()
        await self._session.refresh(model)
        return self._profile(model)

    async def update_avatar(
        self, *, user_id: UUID, avatar_path: str | None
    ) -> UserProfile | None:
        model = await self._session.get(UsuarioModel, user_id)
        if model is None:
            return None
        model.avatar_path = avatar_path
        await self._session.commit()
        await self._session.refresh(model)
        return self._profile(model)

    @staticmethod
    def _profile(model: UsuarioModel) -> UserProfile:
        return UserProfile(
            id=model.id,
            matricula=model.matricula,
            curso_codigo=model.curso_codigo,
            nome=model.nome,
            ppc_id=model.ppc_id,
            data_nascimento=model.data_nascimento,
            avatar_path=model.avatar_path,
        )
