from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    ForeignKey,
    Identity,
    Integer,
    Numeric,
    SmallInteger,
    Table,
    Text,
    Uuid,
    Date,
    DateTime,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


offering_teacher = Table(
    "oferta_docente",
    Base.metadata,
    Column("oferta_turma_id", Uuid(as_uuid=True), ForeignKey("oferta_turma.id"), primary_key=True),
    Column("docente_id", Uuid(as_uuid=True), ForeignKey("docente.id"), primary_key=True),
)


class CursoModel(Base):
    __tablename__ = "curso"
    codigo: Mapped[str] = mapped_column(Text, primary_key=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    ppcs: Mapped[list[CurriculoModel]] = relationship(back_populates="course")
    offerings: Mapped[list[OfertaTurmaModel]] = relationship(back_populates="course")


class DisciplinaModel(Base):
    __tablename__ = "disciplina"
    codigo: Mapped[str] = mapped_column(Text, primary_key=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    curriculum_components: Mapped[list[ComponenteCurricularModel]] = relationship(back_populates="discipline")
    offerings: Mapped[list[OfertaTurmaModel]] = relationship(back_populates="discipline")


class CurriculoModel(Base):
    __tablename__ = "ppc"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    curso_codigo: Mapped[str] = mapped_column(ForeignKey("curso.codigo"), nullable=False)
    ano_versao: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    curriculo_corrente: Mapped[bool] = mapped_column(Boolean, nullable=False)
    periodos_ideais: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    carga_horaria_total: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    carga_horaria_extensao: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    fonte_referencia: Mapped[str] = mapped_column(Text, nullable=False)
    course: Mapped[CursoModel] = relationship(back_populates="ppcs")
    components: Mapped[list[ComponenteCurricularModel]] = relationship(back_populates="curriculum")


class ComponenteCurricularModel(Base):
    __tablename__ = "ppc_componente_curricular"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    ppc_id: Mapped[int] = mapped_column(ForeignKey("ppc.id"), nullable=False)
    disciplina_codigo: Mapped[str | None] = mapped_column(ForeignKey("disciplina.codigo"), nullable=True)
    semestre_recomendado: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ordem_semestre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    tipo_componente: Mapped[str] = mapped_column(Text, nullable=False)
    nome_no_ppc: Mapped[str] = mapped_column(Text, nullable=False)
    carga_horaria: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    curriculum: Mapped[CurriculoModel] = relationship(back_populates="components")
    discipline: Mapped[DisciplinaModel | None] = relationship(back_populates="curriculum_components")


class DocenteModel(Base):
    __tablename__ = "docente"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    offerings: Mapped[list[OfertaTurmaModel]] = relationship(secondary=offering_teacher, back_populates="teachers")


class OfertaTurmaModel(Base):
    __tablename__ = "oferta_turma"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    curso_codigo: Mapped[str] = mapped_column(ForeignKey("curso.codigo"), nullable=False)
    disciplina_codigo: Mapped[str] = mapped_column(ForeignKey("disciplina.codigo"), nullable=False)
    ano: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    semestre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    codigo_turma: Mapped[str] = mapped_column(Text, nullable=False)
    carga_horaria: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    creditos: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    situacao: Mapped[str] = mapped_column(Text, nullable=False)
    course: Mapped[CursoModel] = relationship(back_populates="offerings")
    discipline: Mapped[DisciplinaModel] = relationship(back_populates="offerings")
    teachers: Mapped[list[DocenteModel]] = relationship(secondary=offering_teacher, back_populates="offerings")


class AlunoModel(Base):
    __tablename__ = "aluno"
    matricula: Mapped[str] = mapped_column(Text, primary_key=True)
    nome: Mapped[str] = mapped_column(Text, nullable=False)


class UsuarioModel(Base):
    __tablename__ = "usuario"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    matricula: Mapped[str] = mapped_column(
        ForeignKey("aluno.matricula"), nullable=False, unique=True
    )
    curso_codigo: Mapped[str] = mapped_column(
        ForeignKey("curso.codigo"), nullable=False
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    aceitou_termos_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class MatriculaTurmaModel(Base):
    __tablename__ = "matricula_turma"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    oferta_turma_id: Mapped[UUID] = mapped_column(
        ForeignKey("oferta_turma.id"), nullable=False
    )
    aluno_matricula: Mapped[str] = mapped_column(
        ForeignKey("aluno.matricula"), nullable=False
    )
    curso_aluno_codigo: Mapped[str] = mapped_column(
        ForeignKey("curso.codigo"), nullable=False
    )
    numero_lista: Mapped[int] = mapped_column(Integer, nullable=False)
    faltas_total: Mapped[int] = mapped_column(Integer, nullable=False)
    media_parcial: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    media_final: Mapped[float | None] = mapped_column(Numeric, nullable=True)
    situacao_final: Mapped[str] = mapped_column(Text, nullable=False)
