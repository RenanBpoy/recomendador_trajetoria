from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import PlanoSemanaItem, PlanoSemanaItemInput
from app.models.academic import PlanoSemanaItemModel


class SqlAlchemyPlanoSemanalRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_user(self, user_id: UUID) -> tuple[PlanoSemanaItem, ...]:
        statement = (
            select(PlanoSemanaItemModel)
            .where(PlanoSemanaItemModel.usuario_id == user_id)
            .order_by(
                PlanoSemanaItemModel.dia_semana,
                PlanoSemanaItemModel.hora_inicio,
                PlanoSemanaItemModel.id,
            )
        )
        models = (await self._session.scalars(statement)).all()
        return tuple(self._entity(model) for model in models)

    async def replace_for_user(
        self, *, user_id: UUID, items: tuple[PlanoSemanaItemInput, ...]
    ) -> tuple[PlanoSemanaItem, ...]:
        await self._session.execute(
            delete(PlanoSemanaItemModel).where(
                PlanoSemanaItemModel.usuario_id == user_id
            )
        )
        now = datetime.now(timezone.utc)
        self._session.add_all(
            [
                PlanoSemanaItemModel(
                    usuario_id=user_id,
                    tipo_atividade=item.tipo_atividade,
                    titulo=item.titulo,
                    dia_semana=item.dia_semana,
                    hora_inicio=item.hora_inicio,
                    hora_fim=item.hora_fim,
                    observacoes=item.observacoes,
                    criado_em=now,
                    atualizado_em=now,
                )
                for item in items
            ]
        )
        await self._session.commit()
        return await self.list_by_user(user_id)

    @staticmethod
    def _entity(model: PlanoSemanaItemModel) -> PlanoSemanaItem:
        return PlanoSemanaItem(
            id=model.id,
            tipo_atividade=model.tipo_atividade,
            titulo=model.titulo,
            dia_semana=model.dia_semana,
            hora_inicio=model.hora_inicio,
            hora_fim=model.hora_fim,
            observacoes=model.observacoes,
        )
