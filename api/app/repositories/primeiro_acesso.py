from uuid import UUID

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import ResultadoResetPrimeiroAcesso
from app.models.academic import (
    EquivalenciaManualDisciplinaModel,
    HistoricoImportacaoModel,
    PlanoSemanaItemModel,
    QuestionarioPreenchimentoModel,
)


class SqlAlchemyPrimeiroAcessoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def reset_user_progress(
        self, user_id: UUID
    ) -> ResultadoResetPrimeiroAcesso:
        equivalencias = await self._session.execute(
            delete(EquivalenciaManualDisciplinaModel).where(
                EquivalenciaManualDisciplinaModel.usuario_id == user_id
            )
        )
        historicos = await self._session.execute(
            delete(HistoricoImportacaoModel).where(
                HistoricoImportacaoModel.usuario_id == user_id
            )
        )
        questionarios = await self._session.execute(
            delete(QuestionarioPreenchimentoModel).where(
                QuestionarioPreenchimentoModel.usuario_id == user_id
            )
        )
        plano = await self._session.execute(
            delete(PlanoSemanaItemModel).where(
                PlanoSemanaItemModel.usuario_id == user_id
            )
        )
        await self._session.commit()

        return ResultadoResetPrimeiroAcesso(
            historicos_importados_removidos=max(historicos.rowcount or 0, 0),
            equivalencias_manuais_removidas=max(equivalencias.rowcount or 0, 0),
            questionarios_reiniciados=max(questionarios.rowcount or 0, 0),
            itens_plano_removidos=max(plano.rowcount or 0, 0),
        )
