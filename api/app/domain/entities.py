from dataclasses import dataclass
from datetime import date, datetime, time
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class Page(Generic[T]):
    items: tuple[T, ...]
    next_cursor: str | None = None


@dataclass(frozen=True, slots=True)
class Curso:
    codigo: str
    nome: str


@dataclass(frozen=True, slots=True)
class Disciplina:
    codigo: str
    nome: str


@dataclass(frozen=True, slots=True)
class DisciplinaEquivalencia:
    disciplina_codigo_a: str
    disciplina_codigo_b: str
    criterio: str
    confianca: float


@dataclass(frozen=True, slots=True)
class EstatisticaDisciplina:
    codigo: str
    total_tentativas: int
    total_reprovacoes: int
    taxa_reprovacao: float


@dataclass(frozen=True, slots=True)
class DedicacaoExtraclasseDisciplina:
    codigo: str
    respostas_ate_1h: int
    respostas_entre_1_3h: int
    respostas_mais_3h: int
    total_respostas: int
    faixa_modal: str


@dataclass(frozen=True, slots=True)
class Curriculo:
    id: int
    curso_codigo: str
    ano_versao: int
    nome: str
    curriculo_corrente: bool
    periodos_ideais: int
    carga_horaria_total: int
    carga_horaria_extensao: int
    fonte_referencia: str


@dataclass(frozen=True, slots=True)
class ComponenteCurricular:
    id: int
    ppc_id: int
    disciplina_codigo: str | None
    semestre_recomendado: int
    ordem_semestre: int
    tipo_componente: str
    nome_no_ppc: str
    disciplina_nome: str | None
    carga_horaria: int


@dataclass(frozen=True, slots=True)
class Docente:
    id: UUID
    nome: str


@dataclass(frozen=True, slots=True)
class HorarioOfertaTurma:
    id: int
    dia_semana: int
    dia_nome: str
    hora_inicio: time
    hora_fim: time
    sala: str


@dataclass(frozen=True, slots=True)
class OfertaTurma:
    id: UUID
    curso_codigo: str
    curso_nome: str
    disciplina_codigo: str
    disciplina_nome: str
    ano: int
    semestre: int
    codigo_turma: str
    carga_horaria: int
    creditos: int
    situacao: str
    docentes: tuple[Docente, ...]
    fonte_dados: str = "DIARIO_CLASSE"
    fonte_referencia: str | None = None
    horarios: tuple[HorarioOfertaTurma, ...] = ()


@dataclass(frozen=True, slots=True)
class PeriodoAcademico:
    ano: int
    semestre: int


@dataclass(frozen=True, slots=True)
class ItemHistoricoEscolar:
    matricula: str
    disciplina_codigo: str
    disciplina: str
    professores: str | None
    ano: int
    semestre: int
    codigo_turma: str
    media_final: float | None
    faltas_total: int
    situacao_final: str
    fonte: str = "DIARIO_CLASSE"
    disciplina_codigo_origem: str | None = None
    disciplina_origem: str | None = None
    metodo_correspondencia: str | None = None
    confianca_correspondencia: float | None = None


@dataclass(frozen=True, slots=True)
class ItemHistoricoDocumento:
    codigo: str
    nome: str
    carga_horaria: int
    creditos: int
    situacao: str
    ano: int
    semestre: int
    media: float | None = None
    dispensa: str | None = None
    categoria: str | None = None
    professores: str | None = None


@dataclass(frozen=True, slots=True)
class HistoricoDocumento:
    curso_codigo: str
    ppc_ano: int
    nome_aluno: str
    matricula: str
    data_emissao: date | None
    itens: tuple[ItemHistoricoDocumento, ...]
    media_geral: float | None = None
    carga_horaria_realizada: int | None = None
    carga_horaria_total: int | None = None
    percentual_concluido: float | None = None


@dataclass(frozen=True, slots=True)
class CorrespondenciaProposta:
    item_indice: int
    ppc_id: int
    ppc_componente_id: int
    metodo: str
    confianca: float
    status: str


@dataclass(frozen=True, slots=True)
class ItemImportacaoHistorico:
    id: int
    codigo_original: str
    nome_original: str
    carga_horaria: int
    ano: int
    semestre: int
    situacao: str
    media: float | None
    correspondencia_id: int | None = None
    disciplina_codigo: str | None = None
    disciplina_nome: str | None = None
    metodo_correspondencia: str | None = None
    confianca_correspondencia: float | None = None
    status_correspondencia: str | None = None


@dataclass(frozen=True, slots=True)
class ImportacaoHistorico:
    id: UUID
    nome_arquivo: str
    criado_em: datetime
    curso_codigo_documento: str
    ppc_ano_documento: int
    ppc_referencia_id: int
    total_itens: int
    identificados: int
    requerem_confirmacao: int
    nao_identificados: int
    itens: tuple[ItemImportacaoHistorico, ...]


@dataclass(frozen=True, slots=True)
class CandidatoEquivalencia:
    id: int
    codigo_original: str
    nome_original: str
    carga_horaria: int
    ano: int
    semestre: int
    situacao: str
    media: float | None
    selecionavel: bool = False
    motivo_indisponibilidade: str | None = None
    similaridade_nome: float | None = None
    em_uso: bool = False
    componente_em_uso_id: int | None = None
    slot_em_uso: int | None = None


@dataclass(frozen=True, slots=True)
class EquivalenciaManual:
    id: int
    ppc_id: int
    ppc_componente_id: int
    slot_ordem: int
    historico_item_id: int
    codigo_original: str
    nome_original: str
    carga_horaria: int
    ano: int
    semestre: int
    situacao: str
    media: float | None
    tipo_componente: str
    nome_componente: str
    disciplina_codigo: str | None


@dataclass(frozen=True, slots=True)
class SignupCommand:
    nome: str
    matricula: str
    email: str
    data_nascimento: date
    curso_codigo: str
    senha: str


@dataclass(frozen=True, slots=True)
class AuthUser:
    id: UUID
    email: str


@dataclass(frozen=True, slots=True)
class AuthSession:
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str


@dataclass(frozen=True, slots=True)
class UserProfile:
    id: UUID
    matricula: str
    curso_codigo: str
    nome: str
    ppc_id: int | None = None
    data_nascimento: date | None = None
    avatar_path: str | None = None
    avatar_url: str | None = None


@dataclass(frozen=True, slots=True)
class PlanoSemanaItemInput:
    tipo_atividade: str
    titulo: str
    dia_semana: int
    hora_inicio: time
    hora_fim: time
    observacoes: str | None = None


@dataclass(frozen=True, slots=True)
class PlanoSemanaItem:
    id: int
    tipo_atividade: str
    titulo: str
    dia_semana: int
    hora_inicio: time
    hora_fim: time
    observacoes: str | None = None


@dataclass(frozen=True, slots=True)
class QuestionarioPergunta:
    id: int
    codigo: str
    ordem_global: int
    ordem_secao: int
    texto: str
    peso_recomendacao: float = 1.0
    resposta: int | None = None


@dataclass(frozen=True, slots=True)
class QuestionarioSecao:
    id: int
    codigo: str
    ordem: int
    titulo: str
    descricao: str
    orientacao: str | None
    perguntas: tuple[QuestionarioPergunta, ...]


@dataclass(frozen=True, slots=True)
class QuestionarioPreenchimento:
    id: UUID | None
    status: str
    total_perguntas: int
    total_respondidas: int
    atualizado_em: datetime | None = None
    concluido_em: datetime | None = None


@dataclass(frozen=True, slots=True)
class QuestionarioAtual:
    id: int
    codigo: str
    versao: int
    titulo: str
    descricao: str
    escala_minima: int
    escala_maxima: int
    secoes: tuple[QuestionarioSecao, ...]
    preenchimento: QuestionarioPreenchimento


@dataclass(frozen=True, slots=True)
class SignupResult:
    usuario: AuthUser
    sessao: AuthSession | None
    confirmacao_email_necessaria: bool
    perfil: UserProfile | None = None


@dataclass(frozen=True, slots=True)
class LoginResult:
    usuario: AuthUser
    sessao: AuthSession
    perfil: UserProfile | None = None
