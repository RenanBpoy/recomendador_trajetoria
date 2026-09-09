from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.professores import Professor, TurmaProfessor
from app.models.academic import DocenteModel, DisciplinaModel, OfertaTurmaModel, MatriculaTurmaModel, offering_teacher


class SqlAlchemyProfessoresRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def buscar(self, nome: str, limite: int, inicio: int) -> list[Professor]:
        # Escape dos curingas para pesquisar o texto informado literalmente.
        pattern = nome.replace('\\', '\\\\').replace('%', '\\%').replace('_', '\\_')
        statement = select(DocenteModel).where(DocenteModel.nome.ilike(f'%{pattern}%', escape='\\'))
        rows = await self.session.scalars(statement.order_by(DocenteModel.nome, DocenteModel.id).offset(inicio).limit(limite))
        return [Professor(row.id, row.nome) for row in rows]

    async def obter(self, professor_id: UUID) -> Professor | None:
        row = await self.session.get(DocenteModel, professor_id)
        return Professor(row.id, row.nome) if row else None

    async def turmas(self, professor_id: UUID) -> list[TurmaProfessor]:
        ot, mt = OfertaTurmaModel, MatriculaTurmaModel
        professores_por_turma = (
            select(offering_teacher.c.oferta_turma_id, func.count().label('total_docentes'))
            .group_by(offering_teacher.c.oferta_turma_id).subquery()
        )
        # O filtro é pela oferta_docente, nunca apenas pelo código da disciplina.
        # Não juntamos as matrículas aos demais docentes (evita multiplicar resultados).
        statement = (
            select(
                ot.id, ot.disciplina_codigo, DisciplinaModel.nome.label('disciplina'),
                ot.ano, ot.semestre, ot.codigo_turma,
                func.count(mt.id).label('total_matriculas'),
                func.sum(case((mt.situacao_final.ilike('%aprovado%'), 1), else_=0)).label('aprovados'),
                func.sum(case((mt.situacao_final.ilike('%reprovado%'), 1), else_=0)).label('reprovados'),
                professores_por_turma.c.total_docentes,
            )
            .join(offering_teacher, offering_teacher.c.oferta_turma_id == ot.id)
            .join(DisciplinaModel, DisciplinaModel.codigo == ot.disciplina_codigo)
            .join(professores_por_turma, professores_por_turma.c.oferta_turma_id == ot.id)
            .outerjoin(mt, mt.oferta_turma_id == ot.id)
            .where(offering_teacher.c.docente_id == professor_id)
            .group_by(ot.id, ot.disciplina_codigo, DisciplinaModel.nome, ot.ano, ot.semestre, ot.codigo_turma, professores_por_turma.c.total_docentes)
            .order_by(ot.ano.desc(), ot.semestre.desc(), DisciplinaModel.nome, ot.codigo_turma, ot.id)
        )
        return [TurmaProfessor(**row) for row in (await self.session.execute(statement)).mappings()]
