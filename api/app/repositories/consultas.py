from uuid import UUID
from sqlalchemy import select, func, case, or_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.academic import DisciplinaModel as D, OfertaTurmaModel as O, MatriculaTurmaModel as M, AlunoModel as A


class SqlAlchemyConsultasAcademicasRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def disciplinas(self, busca: str, inicio: int, limite: int) -> list[dict]:
        escaped = busca.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        statement = select(D.codigo, D.nome).where(or_(D.nome.ilike(f'%{escaped}%', escape='\\'), D.codigo.ilike(f'%{escaped}%', escape='\\'))).order_by(D.nome, D.codigo).offset(inicio).limit(limite)
        return [dict(row) for row in (await self.session.execute(statement)).mappings()]

    async def turmas(self, codigo: str) -> list[dict]:
        # Apenas ofertas dos diários que possuam ao menos um resultado de
        # aprovação ou reprovação. Turmas vazias ou somente com situações fora
        # do cálculo não acrescentam informação à consulta da disciplina.
        statement = (
            select(O.id, O.ano, O.semestre, O.codigo_turma, O.curso_codigo, O.carga_horaria)
            .join(M, M.oferta_turma_id == O.id)
            .where(
                O.disciplina_codigo == codigo,
                O.fonte_dados == 'DIARIO_CLASSE',
                or_(
                    M.situacao_final.ilike('%aprovado%'),
                    M.situacao_final.ilike('%reprovado%'),
                ),
            )
            .distinct()
            .order_by(O.ano.desc(), O.semestre.desc(), O.codigo_turma, O.id)
        )
        return [dict(row) for row in (await self.session.execute(statement)).mappings()]

    async def resumo(self, *, codigo: str | None = None, oferta_id: UUID | None = None) -> dict:
        statement = select(
            func.count(M.id).label('total_registros'),
            func.coalesce(func.sum(case((M.situacao_final.ilike('%aprovado%'), 1), else_=0)), 0).label('aprovados'),
            func.coalesce(func.sum(case((M.situacao_final.ilike('%reprovado%'), 1), else_=0)), 0).label('reprovados'),
        ).select_from(M).join(O, O.id == M.oferta_turma_id)
        if codigo is not None:
            statement = statement.where(O.disciplina_codigo == codigo)
        if oferta_id is not None:
            statement = statement.where(O.id == oferta_id)
        return dict((await self.session.execute(statement)).mappings().one())

    async def matriculas(self, oferta_id: UUID, matricula: str | None) -> list[dict]:
        statement = select(A.nome, M.aluno_matricula.label('matricula'), M.curso_aluno_codigo, M.numero_lista, M.faltas_total, M.media_parcial, M.media_final, M.situacao_final).join(A, A.matricula == M.aluno_matricula).where(M.oferta_turma_id == oferta_id)
        # A restrição acontece na consulta, antes de qualquer dado sair do banco.
        if matricula is not None:
            statement = statement.where(M.aluno_matricula == matricula)
        return [dict(row) for row in (await self.session.execute(statement.order_by(M.numero_lista, A.nome))).mappings()]
