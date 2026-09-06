from __future__ import annotations

from datetime import date, datetime, time
from uuid import UUID, uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    Column,
    Computed,
    ForeignKey,
    ForeignKeyConstraint,
    Identity,
    Integer,
    Numeric,
    SmallInteger,
    Table,
    Text,
    Uuid,
    UniqueConstraint,
    Date,
    DateTime,
    Time,
    text,
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


class DisciplinaEquivalenciaModel(Base):
    __tablename__ = "disciplina_equivalencia"
    __table_args__ = (
        CheckConstraint(
            "disciplina_codigo_a < disciplina_codigo_b",
            name="ck_disciplina_equivalencia_ordem",
        ),
        CheckConstraint(
            "criterio in ('NOME_IGUAL', 'SUFIXO_LETRA')",
            name="ck_disciplina_equivalencia_criterio",
        ),
        CheckConstraint(
            "confianca > 0 and confianca <= 1",
            name="ck_disciplina_equivalencia_confianca",
        ),
    )
    disciplina_codigo_a: Mapped[str] = mapped_column(
        ForeignKey("disciplina.codigo"), primary_key=True
    )
    disciplina_codigo_b: Mapped[str] = mapped_column(
        ForeignKey("disciplina.codigo"), primary_key=True
    )
    criterio: Mapped[str] = mapped_column(Text, nullable=False)
    confianca: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


class DisciplinaDedicacaoExtraclasseModel(Base):
    __tablename__ = "disciplina_dedicacao_extraclasse"
    __table_args__ = (
        CheckConstraint(
            "respostas_ate_1h >= 0 and respostas_entre_1_3h >= 0 and respostas_mais_3h >= 0",
            name="ck_disciplina_dedicacao_contagens_nao_negativas",
        ),
    )
    disciplina_codigo: Mapped[str] = mapped_column(
        ForeignKey("disciplina.codigo", onupdate="CASCADE", ondelete="CASCADE"),
        primary_key=True,
    )
    respostas_ate_1h: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    respostas_entre_1_3h: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    respostas_mais_3h: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    total_respostas: Mapped[int] = mapped_column(
        SmallInteger,
        Computed(
            "respostas_ate_1h + respostas_entre_1_3h + respostas_mais_3h",
            persisted=True,
        ),
    )
    faixa_modal: Mapped[str] = mapped_column(
        Text,
        Computed(
            "case "
            "when respostas_mais_3h >= respostas_entre_1_3h "
            "and respostas_mais_3h >= respostas_ate_1h then 'MAIS_DE_3H' "
            "when respostas_entre_1_3h >= respostas_ate_1h then 'ENTRE_1_E_3H' "
            "else 'ATE_1H' end",
            persisted=True,
        ),
    )
    fonte_referencia: Mapped[str] = mapped_column(Text, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=text("now()")
    )


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
    __table_args__ = (
        UniqueConstraint("id", "ppc_id", name="uk_ppc_componente_id_ppc"),
    )
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
    fonte_dados: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="DIARIO_CLASSE"
    )
    fonte_referencia: Mapped[str | None] = mapped_column(Text, nullable=True)
    course: Mapped[CursoModel] = relationship(back_populates="offerings")
    discipline: Mapped[DisciplinaModel] = relationship(back_populates="offerings")
    teachers: Mapped[list[DocenteModel]] = relationship(secondary=offering_teacher, back_populates="offerings")
    schedules: Mapped[list[HorarioOfertaTurmaModel]] = relationship(
        back_populates="offering",
        cascade="all, delete-orphan",
    )


class HorarioOfertaTurmaModel(Base):
    __tablename__ = "oferta_turma_horario"
    id: Mapped[int] = mapped_column(
        BigInteger, Identity(always=True), primary_key=True
    )
    oferta_turma_id: Mapped[UUID] = mapped_column(
        ForeignKey("oferta_turma.id", ondelete="CASCADE"), nullable=False
    )
    dia_semana: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[time] = mapped_column(Time, nullable=False)
    sala: Mapped[str] = mapped_column(Text, nullable=False)
    offering: Mapped[OfertaTurmaModel] = relationship(back_populates="schedules")


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
    ppc_id: Mapped[int | None] = mapped_column(
        ForeignKey("ppc.id"), nullable=True
    )
    nome: Mapped[str] = mapped_column(Text, nullable=False)
    data_nascimento: Mapped[date] = mapped_column(Date, nullable=False)
    avatar_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    aceitou_termos_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class PlanoSemanaItemModel(Base):
    __tablename__ = "plano_semana_item"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    tipo_atividade: Mapped[str] = mapped_column(Text, nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    dia_semana: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    hora_inicio: Mapped[time] = mapped_column(Time, nullable=False)
    hora_fim: Mapped[time] = mapped_column(Time, nullable=False)
    observacoes: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QuestionarioModel(Base):
    __tablename__ = "questionario"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    versao: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    escala_minima: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    escala_maxima: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class QuestionarioSecaoModel(Base):
    __tablename__ = "questionario_secao"
    __table_args__ = (
        UniqueConstraint(
            "id", "questionario_id", name="uk_questionario_secao_id_questionario"
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    questionario_id: Mapped[int] = mapped_column(
        ForeignKey("questionario.id"), nullable=False
    )
    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    titulo: Mapped[str] = mapped_column(Text, nullable=False)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    orientacao: Mapped[str | None] = mapped_column(Text, nullable=True)


class QuestionarioPerguntaModel(Base):
    __tablename__ = "questionario_pergunta"
    __table_args__ = (
        ForeignKeyConstraint(
            ["secao_id", "questionario_id"],
            ["questionario_secao.id", "questionario_secao.questionario_id"],
            name="fk_questionario_pergunta_secao",
        ),
        UniqueConstraint(
            "id", "questionario_id", name="uk_questionario_pergunta_id_questionario"
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    questionario_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    secao_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    codigo: Mapped[str] = mapped_column(Text, nullable=False)
    ordem_global: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ordem_secao: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    texto: Mapped[str] = mapped_column(Text, nullable=False)
    peso_recomendacao: Mapped[float] = mapped_column(
        Numeric(4, 2), nullable=False, server_default="1.00"
    )
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False)


class QuestionarioPreenchimentoModel(Base):
    __tablename__ = "questionario_preenchimento"
    __table_args__ = (
        UniqueConstraint(
            "id",
            "usuario_id",
            "questionario_id",
            name="uk_questionario_preenchimento_vinculo",
        ),
    )
    id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid4
    )
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    questionario_id: Mapped[int] = mapped_column(
        ForeignKey("questionario.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(Text, nullable=False)
    iniciado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    concluido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )


class QuestionarioRespostaModel(Base):
    __tablename__ = "questionario_resposta"
    __table_args__ = (
        ForeignKeyConstraint(
            ["preenchimento_id", "usuario_id", "questionario_id"],
            [
                "questionario_preenchimento.id",
                "questionario_preenchimento.usuario_id",
                "questionario_preenchimento.questionario_id",
            ],
            name="fk_questionario_resposta_preenchimento",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["pergunta_id", "questionario_id"],
            ["questionario_pergunta.id", "questionario_pergunta.questionario_id"],
            name="fk_questionario_resposta_pergunta",
        ),
    )
    preenchimento_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True
    )
    pergunta_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), nullable=False)
    questionario_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    valor: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    respondido_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


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


class HistoricoImportacaoModel(Base):
    __tablename__ = "historico_importacao"
    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, default=uuid4)
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    ppc_referencia_id: Mapped[int] = mapped_column(ForeignKey("ppc.id"), nullable=False)
    nome_arquivo: Mapped[str] = mapped_column(Text, nullable=False)
    hash_arquivo: Mapped[str] = mapped_column(Text, nullable=False)
    curso_codigo_documento: Mapped[str] = mapped_column(Text, nullable=False)
    ppc_ano_documento: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    nome_aluno_documento: Mapped[str] = mapped_column(Text, nullable=False)
    matricula_documento: Mapped[str] = mapped_column(Text, nullable=False)
    data_emissao: Mapped[date | None] = mapped_column(Date, nullable=True)
    media_geral: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    carga_horaria_realizada: Mapped[int | None] = mapped_column(Integer, nullable=True)
    carga_horaria_total: Mapped[int | None] = mapped_column(Integer, nullable=True)
    percentual_concluido: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    ativa: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    total_itens: Mapped[int] = mapped_column(Integer, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ItemHistoricoImportadoModel(Base):
    __tablename__ = "historico_importado_item"
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    importacao_id: Mapped[UUID] = mapped_column(
        ForeignKey("historico_importacao.id", ondelete="CASCADE"), nullable=False
    )
    codigo_original: Mapped[str] = mapped_column(Text, nullable=False)
    nome_original: Mapped[str] = mapped_column(Text, nullable=False)
    carga_horaria: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    creditos: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    ano: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    semestre: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    situacao: Mapped[str] = mapped_column(Text, nullable=False)
    media: Mapped[float | None] = mapped_column(Numeric(4, 2), nullable=True)
    dispensa: Mapped[str | None] = mapped_column(Text, nullable=True)
    categoria: Mapped[str | None] = mapped_column(Text, nullable=True)
    professores: Mapped[str | None] = mapped_column(Text, nullable=True)


class CorrespondenciaDisciplinaModel(Base):
    __tablename__ = "correspondencia_disciplina"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ppc_componente_id", "ppc_id"],
            ["ppc_componente_curricular.id", "ppc_componente_curricular.ppc_id"],
            name="fk_correspondencia_componente_ppc",
            ondelete="CASCADE",
        ),
        UniqueConstraint("item_id", "ppc_id", name="uk_correspondencia_item_ppc"),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    item_id: Mapped[int] = mapped_column(
        ForeignKey("historico_importado_item.id", ondelete="CASCADE"), nullable=False
    )
    ppc_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    ppc_componente_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    metodo: Mapped[str] = mapped_column(Text, nullable=False)
    confianca: Mapped[float] = mapped_column(Numeric(5, 4), nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revisado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class EquivalenciaManualDisciplinaModel(Base):
    __tablename__ = "equivalencia_manual_disciplina"
    __table_args__ = (
        ForeignKeyConstraint(
            ["ppc_componente_id", "ppc_id"],
            ["ppc_componente_curricular.id", "ppc_componente_curricular.ppc_id"],
            name="fk_equivalencia_manual_componente_ppc",
            ondelete="CASCADE",
        ),
        UniqueConstraint(
            "usuario_id",
            "ppc_id",
            "ppc_componente_id",
            "slot_ordem",
            name="uk_equivalencia_manual_slot",
        ),
        UniqueConstraint(
            "usuario_id",
            "ppc_id",
            "historico_item_id",
            name="uk_equivalencia_manual_item",
        ),
    )
    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    usuario_id: Mapped[UUID] = mapped_column(
        ForeignKey("usuario.id", ondelete="CASCADE"), nullable=False
    )
    ppc_id: Mapped[int] = mapped_column(
        ForeignKey("ppc.id", ondelete="CASCADE"), nullable=False
    )
    ppc_componente_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    slot_ordem: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    historico_item_id: Mapped[int] = mapped_column(
        ForeignKey("historico_importado_item.id", ondelete="CASCADE"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
