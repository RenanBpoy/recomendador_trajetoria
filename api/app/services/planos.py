from uuid import UUID

from app.core.errors import ApplicationError
from app.domain.entities import PlanoSemanaItem, PlanoSemanaItemInput
from app.domain.ports import PlanoSemanalRepository


class PlanoSemanalService:
    def __init__(self, repository: PlanoSemanalRepository) -> None:
        self._repository = repository

    async def get(self, user_id: UUID) -> tuple[PlanoSemanaItem, ...]:
        return await self._repository.list_by_user(user_id)

    async def replace(
        self, *, user_id: UUID, items: tuple[PlanoSemanaItemInput, ...]
    ) -> tuple[PlanoSemanaItem, ...]:
        self._validate_no_overlaps(items)
        return await self._repository.replace_for_user(user_id=user_id, items=items)

    @staticmethod
    def _validate_no_overlaps(items: tuple[PlanoSemanaItemInput, ...]) -> None:
        for day in range(1, 6):
            day_items = sorted(
                (item for item in items if item.dia_semana == day),
                key=lambda item: (item.hora_inicio, item.hora_fim),
            )
            for previous, current in zip(day_items, day_items[1:]):
                if current.hora_inicio < previous.hora_fim:
                    raise ApplicationError(
                        "Existem atividades sobrepostas no mesmo dia.",
                        code="weekly_plan_overlap",
                        details={
                            "dia_semana": day,
                            "atividades": [previous.titulo, current.titulo],
                        },
                    )
