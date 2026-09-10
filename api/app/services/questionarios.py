from uuid import UUID

from app.core.errors import ApplicationError, ResourceNotFoundError
from app.domain.entities import QuestionarioAtual
from app.domain.ports import QuestionarioRepository


class QuestionarioService:
    def __init__(self, repository: QuestionarioRepository) -> None:
        self._repository = repository

    async def get_current(self, user_id: UUID) -> QuestionarioAtual:
        questionario = await self._repository.get_active(user_id)
        if questionario is None:
            raise ResourceNotFoundError("Questionário ativo", "atual")
        return questionario

    async def save_answer(
        self, *, user_id: UUID, pergunta_id: int, valor: int
    ) -> QuestionarioAtual:
        questionario = await self.get_current(user_id)
        if not questionario.escala_minima <= valor <= questionario.escala_maxima:
            raise ApplicationError(
                "A resposta deve estar entre 1 e 10.",
                code="questionario_resposta_fora_escala",
            )

        perguntas = {
            pergunta.id
            for secao in questionario.secoes
            for pergunta in secao.perguntas
        }
        if pergunta_id not in perguntas:
            raise ResourceNotFoundError("Pergunta do questionário", pergunta_id)

        await self._repository.save_answer(
            user_id=user_id,
            questionario_id=questionario.id,
            pergunta_id=pergunta_id,
            valor=valor,
        )
        return await self.get_current(user_id)

    async def submit(self, user_id: UUID, questionario_id: int, respostas: dict[int, int]) -> QuestionarioAtual:
        questionario = await self.get_current(user_id)
        perguntas = {p.id for s in questionario.secoes for p in s.perguntas}
        if questionario.id != questionario_id or set(respostas) != perguntas:
            raise ApplicationError(
                "Responda todas as afirmações do questionário atual antes de concluir.",
                code="questionario_incompleto",
            )
        if any(not questionario.escala_minima <= valor <= questionario.escala_maxima for valor in respostas.values()):
            raise ApplicationError("A resposta deve estar entre 1 e 10.", code="questionario_resposta_fora_escala")
        await self._repository.save_complete(user_id=user_id, questionario_id=questionario.id, respostas=respostas)
        return await self.get_current(user_id)

    async def complete(self, user_id: UUID) -> QuestionarioAtual:
        questionario = await self.get_current(user_id)
        preenchimento = questionario.preenchimento
        if preenchimento.total_respondidas != preenchimento.total_perguntas:
            perguntas_pendentes = [
                pergunta.id
                for secao in questionario.secoes
                for pergunta in secao.perguntas
                if pergunta.resposta is None
            ]
            raise ApplicationError(
                "Responda todas as afirmações antes de concluir o questionário.",
                code="questionario_incompleto",
                details={
                    "total_perguntas": preenchimento.total_perguntas,
                    "total_respondidas": preenchimento.total_respondidas,
                    "perguntas_pendentes": perguntas_pendentes,
                },
            )

        await self._repository.complete(
            user_id=user_id,
            questionario_id=questionario.id,
        )
        return await self.get_current(user_id)
