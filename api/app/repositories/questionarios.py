from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.entities import (
    QuestionarioAtual,
    QuestionarioPergunta,
    QuestionarioPreenchimento,
    QuestionarioSecao,
)
from app.models.academic import (
    QuestionarioModel,
    QuestionarioPerguntaModel,
    QuestionarioPreenchimentoModel,
    QuestionarioRespostaModel,
    QuestionarioSecaoModel,
)


class SqlAlchemyQuestionarioRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_active(self, user_id: UUID) -> QuestionarioAtual | None:
        questionario = await self._session.scalar(
            select(QuestionarioModel).where(QuestionarioModel.ativo.is_(True))
        )
        if questionario is None:
            return None

        preenchimento = await self._session.scalar(
            select(QuestionarioPreenchimentoModel).where(
                QuestionarioPreenchimentoModel.usuario_id == user_id,
                QuestionarioPreenchimentoModel.questionario_id == questionario.id,
            )
        )

        statement = (
            select(
                QuestionarioSecaoModel,
                QuestionarioPerguntaModel,
                QuestionarioRespostaModel.valor,
            )
            .join(
                QuestionarioPerguntaModel,
                and_(
                    QuestionarioPerguntaModel.secao_id == QuestionarioSecaoModel.id,
                    QuestionarioPerguntaModel.questionario_id
                    == QuestionarioSecaoModel.questionario_id,
                ),
            )
            .outerjoin(
                QuestionarioRespostaModel,
                and_(
                    QuestionarioRespostaModel.pergunta_id
                    == QuestionarioPerguntaModel.id,
                    QuestionarioRespostaModel.questionario_id == questionario.id,
                    QuestionarioRespostaModel.usuario_id == user_id,
                ),
            )
            .where(
                QuestionarioSecaoModel.questionario_id == questionario.id,
                QuestionarioPerguntaModel.ativa.is_(True),
            )
            .order_by(
                QuestionarioSecaoModel.ordem,
                QuestionarioPerguntaModel.ordem_secao,
            )
        )
        rows = (await self._session.execute(statement)).all()

        section_models: dict[int, QuestionarioSecaoModel] = {}
        section_questions: dict[int, list[QuestionarioPergunta]] = {}
        total_respondidas = 0
        for section, question, answer in rows:
            section_models[section.id] = section
            section_questions.setdefault(section.id, []).append(
                QuestionarioPergunta(
                    id=question.id,
                    codigo=question.codigo,
                    ordem_global=question.ordem_global,
                    ordem_secao=question.ordem_secao,
                    texto=question.texto,
                    resposta=answer,
                )
            )
            if answer is not None:
                total_respondidas += 1

        secoes = tuple(
            QuestionarioSecao(
                id=section.id,
                codigo=section.codigo,
                ordem=section.ordem,
                titulo=section.titulo,
                descricao=section.descricao,
                orientacao=section.orientacao,
                perguntas=tuple(section_questions.get(section.id, ())),
            )
            for section in sorted(section_models.values(), key=lambda item: item.ordem)
        )
        total_perguntas = sum(len(section.perguntas) for section in secoes)

        return QuestionarioAtual(
            id=questionario.id,
            codigo=questionario.codigo,
            versao=questionario.versao,
            titulo=questionario.titulo,
            descricao=questionario.descricao,
            escala_minima=questionario.escala_minima,
            escala_maxima=questionario.escala_maxima,
            secoes=secoes,
            preenchimento=QuestionarioPreenchimento(
                id=preenchimento.id if preenchimento else None,
                status=preenchimento.status if preenchimento else "NAO_INICIADO",
                total_perguntas=total_perguntas,
                total_respondidas=total_respondidas,
                atualizado_em=preenchimento.atualizado_em if preenchimento else None,
                concluido_em=preenchimento.concluido_em if preenchimento else None,
            ),
        )

    async def save_answer(
        self,
        *,
        user_id: UUID,
        questionario_id: int,
        pergunta_id: int,
        valor: int,
    ) -> None:
        now = datetime.now(timezone.utc)
        preenchimento = await self._session.scalar(
            select(QuestionarioPreenchimentoModel).where(
                QuestionarioPreenchimentoModel.usuario_id == user_id,
                QuestionarioPreenchimentoModel.questionario_id == questionario_id,
            )
        )
        if preenchimento is None:
            preenchimento = QuestionarioPreenchimentoModel(
                usuario_id=user_id,
                questionario_id=questionario_id,
                status="EM_ANDAMENTO",
                iniciado_em=now,
                atualizado_em=now,
                concluido_em=None,
            )
            self._session.add(preenchimento)
            await self._session.flush()

        resposta = await self._session.scalar(
            select(QuestionarioRespostaModel).where(
                QuestionarioRespostaModel.preenchimento_id == preenchimento.id,
                QuestionarioRespostaModel.pergunta_id == pergunta_id,
            )
        )
        if resposta is None:
            self._session.add(
                QuestionarioRespostaModel(
                    preenchimento_id=preenchimento.id,
                    usuario_id=user_id,
                    questionario_id=questionario_id,
                    pergunta_id=pergunta_id,
                    valor=valor,
                    respondido_em=now,
                    atualizado_em=now,
                )
            )
        else:
            resposta.valor = valor
            resposta.atualizado_em = now

        preenchimento.atualizado_em = now
        await self._session.commit()

    async def complete(self, *, user_id: UUID, questionario_id: int) -> None:
        preenchimento = await self._session.scalar(
            select(QuestionarioPreenchimentoModel).where(
                QuestionarioPreenchimentoModel.usuario_id == user_id,
                QuestionarioPreenchimentoModel.questionario_id == questionario_id,
            )
        )
        if preenchimento is None:
            return
        now = datetime.now(timezone.utc)
        preenchimento.status = "CONCLUIDO"
        preenchimento.atualizado_em = now
        preenchimento.concluido_em = now
        await self._session.commit()
