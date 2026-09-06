from datetime import time
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RecomendacaoSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class ContextoSemestreOut(RecomendacaoSchema):
    matricula: str
    regra_matricula: str
    prefixo_ingresso: str
    ano_ingresso: int
    semestre_ingresso: int
    ano_alvo: int
    semestre_alvo: int
    semestre_cronologico: int
    semestre_curricular: int
    regra_semestre_curricular: str
    curso_codigo: str
    ppc_id: int
    ppc_ano: int
    ppc_nome: str


class PesoQuestionarioAplicadoOut(RecomendacaoSchema):
    codigo: str
    texto: str
    peso: float
    resposta: int | None
    contribuicao_normalizada: float | None


class ResumoDesempenhoOut(RecomendacaoSchema):
    tentativas_recentes: int
    aprovacoes_recentes: int
    taxa_aprovacao_recente: float
    disciplinas_dificeis_cursadas: int
    disciplinas_dificeis_aprovadas: int
    limite_disciplinas_alto_risco: int


class HorarioRecomendadoOut(RecomendacaoSchema):
    id: int
    dia_semana: int
    dia_nome: str
    hora_inicio: time
    hora_fim: time
    sala: str


class IndicadorDedicacaoExtraclasseOut(RecomendacaoSchema):
    nivel: Literal["media", "elevada"]
    titulo: str
    descricao: str
    total_respostas: int


class DisciplinaRecomendadaOut(RecomendacaoSchema):
    componente_id: int
    disciplina_codigo: str
    oferta_disciplina_codigo: str
    equivalencia_utilizada: bool
    disciplina_nome: str
    semestre_recomendado: int
    atrasada: bool
    adiantada: bool
    oferta_turma_id: UUID
    codigo_turma: str
    carga_horaria: int
    horas_semanais: float
    taxa_reprovacao: float | None
    amostra_taxa_reprovacao: int
    nivel_risco: Literal["baixo", "medio", "alto", "desconhecido"]
    pontuacao: float
    justificativa: str
    motivos: list[str]
    alertas: list[str]
    horarios: list[HorarioRecomendadoOut]
    dedicacao_extraclasse: IndicadorDedicacaoExtraclasseOut | None = None


class DisciplinaNaoSelecionadaOut(RecomendacaoSchema):
    disciplina_codigo: str
    disciplina_nome: str
    semestre_recomendado: int
    motivo_codigo: str
    motivo: str


class RecomendacaoAtualOut(RecomendacaoSchema):
    titulo: str
    mensagem: str
    contexto: ContextoSemestreOut
    carga_horaria_total: int
    horas_semanais: float
    limite_horas_semanais: float
    indice_questionario: float | None
    questionario_concluido: bool
    plano_semanal_considerado: bool
    desempenho: ResumoDesempenhoOut
    pesos_questionario: list[PesoQuestionarioAplicadoOut]
    disciplinas: list[DisciplinaRecomendadaOut]
    nao_selecionadas: list[DisciplinaNaoSelecionadaOut]
    criterios: list[str]
    alertas: list[str]
