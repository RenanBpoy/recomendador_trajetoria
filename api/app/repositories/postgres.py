from uuid import UUID

from sqlalchemy import Select, desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from app.domain.entities import (
    ComponenteCurricular,
    Curriculo,
    Curso,
    Disciplina,
    Docente,
    ItemHistoricoEscolar,
    OfertaTurma,
    Page,
    PeriodoAcademico,
)
from app.models.academic import (
    AlunoModel,
    ComponenteCurricularModel,
    CurriculoModel,
    CursoModel,
    DisciplinaModel,
    DocenteModel,
    MatriculaTurmaModel,
    OfertaTurmaModel,
    offering_teacher,
)


def _course(model: CursoModel) -> Curso:
    return Curso(codigo=model.codigo, nome=model.nome)


def _discipline(model: DisciplinaModel) -> Disciplina:
    return Disciplina(codigo=model.codigo, nome=model.nome)


def _curriculum(model: CurriculoModel) -> Curriculo:
    return Curriculo(
        id=model.id,
        curso_codigo=model.curso_codigo,
        ano_versao=model.ano_versao,
        nome=model.nome,
        curriculo_corrente=model.curriculo_corrente,
        periodos_ideais=model.periodos_ideais,
        carga_horaria_total=model.carga_horaria_total,
        carga_horaria_extensao=model.carga_horaria_extensao,
        fonte_referencia=model.fonte_referencia,
    )


def _offering(model: OfertaTurmaModel) -> OfertaTurma:
    return OfertaTurma(
        id=model.id,
        curso_codigo=model.curso_codigo,
        curso_nome=model.course.nome,
        disciplina_codigo=model.disciplina_codigo,
        disciplina_nome=model.discipline.nome,
        ano=model.ano,
        semestre=model.semestre,
        codigo_turma=model.codigo_turma,
        carga_horaria=model.carga_horaria,
        creditos=model.creditos,
        situacao=model.situacao,
        docentes=tuple(
            Docente(id=teacher.id, nome=teacher.nome)
            for teacher in sorted(model.teachers, key=lambda item: item.nome)
        ),
    )


class SqlAlchemyCursoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, *, limit: int, cursor: str | None = None) -> Page[Curso]:
        statement = select(CursoModel).order_by(CursoModel.codigo).limit(limit + 1)
        if cursor:
            statement = statement.where(CursoModel.codigo > cursor)
        models = list((await self._session.scalars(statement)).all())
        has_more = len(models) > limit
        items = tuple(_course(model) for model in models[:limit])
        return Page(items=items, next_cursor=items[-1].codigo if has_more else None)

    async def get(self, codigo: str) -> Curso | None:
        model = await self._session.get(CursoModel, codigo)
        return _course(model) if model else None


class SqlAlchemyCurriculoRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_by_course(self, curso_codigo: str) -> tuple[Curriculo, ...]:
        statement = select(CurriculoModel).where(CurriculoModel.curso_codigo == curso_codigo).order_by(desc(CurriculoModel.ano_versao))
        models = (await self._session.scalars(statement)).all()
        return tuple(_curriculum(model) for model in models)

    async def get(self, ppc_id: int) -> Curriculo | None:
        model = await self._session.get(CurriculoModel, ppc_id)
        return _curriculum(model) if model else None

    async def list_components(self, ppc_id: int) -> tuple[ComponenteCurricular, ...]:
        statement = (
            select(ComponenteCurricularModel, DisciplinaModel.nome)
            .outerjoin(DisciplinaModel, DisciplinaModel.codigo == ComponenteCurricularModel.disciplina_codigo)
            .where(ComponenteCurricularModel.ppc_id == ppc_id)
            .order_by(ComponenteCurricularModel.semestre_recomendado, ComponenteCurricularModel.ordem_semestre)
        )
        rows = (await self._session.execute(statement)).all()
        return tuple(
            ComponenteCurricular(
                id=model.id,
                ppc_id=model.ppc_id,
                disciplina_codigo=model.disciplina_codigo,
                semestre_recomendado=model.semestre_recomendado,
                ordem_semestre=model.ordem_semestre,
                tipo_componente=model.tipo_componente,
                nome_no_ppc=model.nome_no_ppc,
                disciplina_nome=discipline_name,
                carga_horaria=model.carga_horaria,
            )
            for model, discipline_name in rows
        )


class SqlAlchemyDisciplinaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, *, limit: int, cursor: str | None = None) -> Page[Disciplina]:
        statement = select(DisciplinaModel).order_by(DisciplinaModel.codigo).limit(limit + 1)
        if cursor:
            statement = statement.where(DisciplinaModel.codigo > cursor)
        models = list((await self._session.scalars(statement)).all())
        has_more = len(models) > limit
        items = tuple(_discipline(model) for model in models[:limit])
        return Page(items=items, next_cursor=items[-1].codigo if has_more else None)

    async def get(self, codigo: str) -> Disciplina | None:
        model = await self._session.get(DisciplinaModel, codigo)
        return _discipline(model) if model else None


class SqlAlchemyOfertaTurmaRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @staticmethod
    def _with_related(statement: Select) -> Select:
        return statement.options(
            joinedload(OfertaTurmaModel.course),
            joinedload(OfertaTurmaModel.discipline),
            selectinload(OfertaTurmaModel.teachers),
        )

    async def list(
        self,
        *,
        limit: int,
        cursor: UUID | None = None,
        curso_codigo: str | None = None,
        disciplina_codigo: str | None = None,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> Page[OfertaTurma]:
        statement = self._with_related(select(OfertaTurmaModel).order_by(OfertaTurmaModel.id).limit(limit + 1))
        filters = {
            OfertaTurmaModel.curso_codigo: curso_codigo,
            OfertaTurmaModel.disciplina_codigo: disciplina_codigo,
            OfertaTurmaModel.ano: ano,
            OfertaTurmaModel.semestre: semestre,
        }
        for column, value in filters.items():
            if value is not None:
                statement = statement.where(column == value)
        if cursor is not None:
            statement = statement.where(OfertaTurmaModel.id > cursor)
        models = list((await self._session.scalars(statement)).all())
        has_more = len(models) > limit
        items = tuple(_offering(model) for model in models[:limit])
        return Page(items=items, next_cursor=str(items[-1].id) if has_more else None)

    async def get(self, offering_id: UUID) -> OfertaTurma | None:
        statement = self._with_related(select(OfertaTurmaModel).where(OfertaTurmaModel.id == offering_id))
        model = (await self._session.scalars(statement)).one_or_none()
        return _offering(model) if model else None

    async def list_periods(self) -> tuple[PeriodoAcademico, ...]:
        statement = select(OfertaTurmaModel.ano, OfertaTurmaModel.semestre).distinct().order_by(desc(OfertaTurmaModel.ano), desc(OfertaTurmaModel.semestre))
        rows = (await self._session.execute(statement)).all()
        return tuple(PeriodoAcademico(ano=ano, semestre=semestre) for ano, semestre in rows)


class SqlAlchemyHistoricoEscolarRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_student(
        self, matricula: str
    ) -> tuple[ItemHistoricoEscolar, ...] | None:
        student = await self._session.get(AlunoModel, matricula)
        if student is None:
            return None

        statement = (
            select(
                MatriculaTurmaModel.id.label("enrollment_id"),
                MatriculaTurmaModel.aluno_matricula.label("matricula"),
                DisciplinaModel.codigo.label("disciplina_codigo"),
                DisciplinaModel.nome.label("disciplina"),
                OfertaTurmaModel.ano,
                OfertaTurmaModel.semestre,
                OfertaTurmaModel.codigo_turma,
                MatriculaTurmaModel.media_final,
                MatriculaTurmaModel.faltas_total,
                MatriculaTurmaModel.situacao_final,
                DocenteModel.nome.label("professor"),
            )
            .join(
                OfertaTurmaModel,
                OfertaTurmaModel.id == MatriculaTurmaModel.oferta_turma_id,
            )
            .join(
                DisciplinaModel,
                DisciplinaModel.codigo == OfertaTurmaModel.disciplina_codigo,
            )
            .outerjoin(
                offering_teacher,
                offering_teacher.c.oferta_turma_id == OfertaTurmaModel.id,
            )
            .outerjoin(
                DocenteModel,
                DocenteModel.id == offering_teacher.c.docente_id,
            )
            .where(MatriculaTurmaModel.aluno_matricula == matricula)
            .order_by(
                OfertaTurmaModel.ano,
                OfertaTurmaModel.semestre,
                DisciplinaModel.nome,
                DocenteModel.nome,
            )
        )
        rows = (await self._session.execute(statement)).all()

        grouped: dict[UUID, dict[str, object]] = {}
        for row in rows:
            entry = grouped.setdefault(
                row.enrollment_id,
                {
                    "matricula": row.matricula,
                    "disciplina_codigo": row.disciplina_codigo,
                    "disciplina": row.disciplina,
                    "ano": row.ano,
                    "semestre": row.semestre,
                    "codigo_turma": row.codigo_turma,
                    "media_final": (
                        float(row.media_final) if row.media_final is not None else None
                    ),
                    "faltas_total": row.faltas_total,
                    "situacao_final": row.situacao_final,
                    "professores": set(),
                },
            )
            if row.professor:
                entry["professores"].add(row.professor)

        return tuple(
            ItemHistoricoEscolar(
                matricula=str(entry["matricula"]),
                disciplina_codigo=str(entry["disciplina_codigo"]),
                disciplina=str(entry["disciplina"]),
                professores=(
                    ", ".join(sorted(entry["professores"]))
                    if entry["professores"]
                    else None
                ),
                ano=int(entry["ano"]),
                semestre=int(entry["semestre"]),
                codigo_turma=str(entry["codigo_turma"]),
                media_final=entry["media_final"],
                faltas_total=int(entry["faltas_total"]),
                situacao_final=str(entry["situacao_final"]),
            )
            for entry in grouped.values()
        )
