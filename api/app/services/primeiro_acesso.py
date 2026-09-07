from uuid import UUID

from app.domain.entities import ResultadoResetPrimeiroAcesso
from app.domain.ports import PrimeiroAcessoRepository


class PrimeiroAcessoService:
    def __init__(self, repository: PrimeiroAcessoRepository) -> None:
        self._repository = repository

    async def reset(self, user_id: UUID) -> ResultadoResetPrimeiroAcesso:
        return await self._repository.reset_user_progress(user_id)
