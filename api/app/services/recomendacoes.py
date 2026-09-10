"""Primeira versão do motor explicável de recomendação acadêmica.

Este é o ponto central para consultar e ajustar as regras. O motor não usa
aprendizado de máquina nesta etapa: combina PPC, pendências, ofertas, horários,
plano semanal, histórico, taxa de reprovação e questionário por regras
determinísticas. Nenhuma recomendação é gravada; ela é recalculada com os dados
atuais para continuar rastreável.

Período de ingresso e semestre curricular
------------------------------------------
Os quatro primeiros dígitos representam o ano de ingresso e o quinto dígito
representa o semestre (1 ou 2). Exemplo: 20232... = ingresso em 2023/2.
A matrícula define apenas o semestre cronológico. Para recomendar, o semestre
curricular é o primeiro período do PPC com menos de 50% da carga horária
obrigatória aprovada. Uma pendência isolada, portanto, não impede o avanço.

Pesos iniciais do questionário
------------------------------
0,8  desempenho em dois turnos
1,5  tempo de estudo extraclasse
1,5  responsabilidades permitem várias disciplinas
1,2  tolerância a semanas intensas
1,0  estudo independente
0,8  busca por ajuda
1,2  antecedência e prazos
1,0  persistência

Os pesos persistidos em ``questionario_pergunta.peso_recomendacao`` são a
fonte efetivamente usada no cálculo. As respostas são normalizadas entre 0 e 1
antes da média ponderada.

Adiantamento de disciplinas
----------------------------
Depois das disciplinas do semestre atual e das pendências, o motor pode
recomendar obrigatórias de semestres futuros. O adiantamento exige taxa de
reprovação conhecida abaixo de 25%, oferta com horário, ausência de conflito e
espaço no limite semanal calculado. A disciplina adiantada não recebe o bônus
de 20 pontos reservado às matérias do semestre atual.

Trabalhos de conclusão
----------------------
Componentes relacionados a TCC, trabalho de conclusão ou trabalho de
graduação ficam fora do cálculo. Eles não são recomendados e também não são
incluídos entre as disciplinas não selecionadas.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import time
from typing import Iterable
from unicodedata import combining, normalize
from uuid import UUID

from app.core.errors import ApplicationError, ResourceNotFoundError
from app.domain.entities import (
    ComponenteCurricular,
    Curriculo,
    DedicacaoExtraclasseDisciplina,
    DisciplinaEquivalencia,
    EstatisticaDisciplina,
    ItemHistoricoEscolar,
    OfertaTurma,
    PlanoSemanaItem,
    QuestionarioAtual,
    UserProfile,
)
from app.domain.ports import (
    AcademicDataProvider,
    PlanoSemanalRepository,
    QuestionarioRepository,
)


REGRA_MATRICULA = (
    "Os quatro primeiros dígitos da matrícula indicam o ano de ingresso e "
    "o quinto dígito indica o semestre de ingresso (1 ou 2)."
)
REGRA_SEMESTRE_CURRICULAR = (
    "O semestre curricular é o primeiro período do PPC com menos de 50% da "
    "carga horária obrigatória aprovada. Com 50% ou mais, o período é considerado "
    "consolidado e as disciplinas restantes passam a ser tratadas como atrasadas, "
    "sempre respeitando o limite do semestre cronológico."
)

PESOS_INICIAIS_QUESTIONARIO = {
    "ROTINA_DESEMPENHO_DOIS_TURNOS": 0.8,
    "ROTINA_TEMPO_ESTUDO_EXTRACLASSE": 1.5,
    "ROTINA_RESPONSABILIDADES_CARGA": 1.5,
    "ROTINA_SEMANAS_INTENSAS": 1.2,
    "FORMACAO_ESTUDO_INDEPENDENTE": 1.0,
    "MOTIVACAO_BUSCA_AJUDA": 0.8,
    "MOTIVACAO_ANTECEDENCIA_PRAZOS": 1.2,
    "MOTIVACAO_PERSISTENCIA": 1.0,
}

LIMITE_BASE_HORAS_SEMANAIS = 16.0
LIMITE_MINIMO_HORAS_SEMANAIS = 12.0
LIMITE_MAXIMO_HORAS_SEMANAIS = 24.0
TAXA_RISCO_MEDIO = 25.0
TAXA_RISCO_ALTO = 40.0
LIMIAR_SEMESTRE_CONSOLIDADO = 0.50
TERMOS_TRABALHO_CONCLUSAO = (
    "trabalho de conclusao",
    "trabalho de graduacao",
    "trabalho final de graduacao",
    "trabalho final de curso",
    "projeto de conclusao",
    "projeto final de curso",
    "monografia",
)


@dataclass(frozen=True, slots=True)
class ContextoSemestre:
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


@dataclass(frozen=True, slots=True)
class PesoQuestionarioAplicado:
    codigo: str
    texto: str
    peso: float
    resposta: int | None
    contribuicao_normalizada: float | None


@dataclass(frozen=True, slots=True)
class ResumoDesempenho:
    tentativas_recentes: int
    aprovacoes_recentes: int
    taxa_aprovacao_recente: float
    disciplinas_dificeis_cursadas: int
    disciplinas_dificeis_aprovadas: int
    limite_disciplinas_alto_risco: int


@dataclass(frozen=True, slots=True)
class HorarioRecomendado:
    id: int
    dia_semana: int
    dia_nome: str
    hora_inicio: time
    hora_fim: time
    sala: str


@dataclass(frozen=True, slots=True)
class IndicadorDedicacaoExtraclasse:
    nivel: str
    titulo: str
    descricao: str
    total_respostas: int


@dataclass(frozen=True, slots=True)
class DisciplinaRecomendada:
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
    nivel_risco: str
    pontuacao: float
    justificativa: str
    motivos: tuple[str, ...]
    alertas: tuple[str, ...]
    horarios: tuple[HorarioRecomendado, ...]
    dedicacao_extraclasse: IndicadorDedicacaoExtraclasse | None = None


@dataclass(frozen=True, slots=True)
class DisciplinaNaoSelecionada:
    disciplina_codigo: str
    disciplina_nome: str
    semestre_recomendado: int
    motivo_codigo: str
    motivo: str


@dataclass(frozen=True, slots=True)
class RecomendacaoAtual:
    titulo: str
    mensagem: str
    contexto: ContextoSemestre
    carga_horaria_total: int
    horas_semanais: float
    limite_horas_semanais: float
    indice_questionario: float | None
    questionario_concluido: bool
    plano_semanal_considerado: bool
    desempenho: ResumoDesempenho
    pesos_questionario: tuple[PesoQuestionarioAplicado, ...]
    disciplinas: tuple[DisciplinaRecomendada, ...]
    nao_selecionadas: tuple[DisciplinaNaoSelecionada, ...]
    criterios: tuple[str, ...]
    alertas: tuple[str, ...]


class RecomendacaoService:
    def __init__(
        self,
        provider: AcademicDataProvider,
        planos: PlanoSemanalRepository,
        questionarios: QuestionarioRepository,
    ) -> None:
        self._provider = provider
        self._planos = planos
        self._questionarios = questionarios

    async def get_context(
        self,
        profile: UserProfile,
        *,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> ContextoSemestre:
        curriculum = await self._get_curriculum(profile)
        ano_alvo, semestre_alvo = await self._target_period(ano, semestre)
        components = self._recommendation_components(
            await self._provider.list_curriculum_components(curriculum.id)
        )
        history = await self._provider.get_school_history(profile.matricula)
        equivalences = await self._provider.list_discipline_equivalences()
        return self._build_context(
            profile,
            curriculum,
            ano_alvo,
            semestre_alvo,
            components,
            history or (),
            equivalences,
        )

    def _build_context(
        self,
        profile: UserProfile,
        curriculum: Curriculo,
        ano_alvo: int,
        semestre_alvo: int,
        components: tuple[ComponenteCurricular, ...],
        history: tuple[ItemHistoricoEscolar, ...],
        equivalences: tuple[DisciplinaEquivalencia, ...],
    ) -> ContextoSemestre:
        ano_ingresso, semestre_ingresso, prefixo = self._parse_registration(profile.matricula)
        semestre_cronologico = self._semester_number(
            ano_ingresso, semestre_ingresso, ano_alvo, semestre_alvo
        )
        latest_history = self._latest_attempts(history)
        equivalent_codes = self._equivalent_codes_map(equivalences)
        semestre_curricular = self._effective_curricular_semester(
            components,
            latest_history,
            equivalent_codes,
            semestre_cronologico,
            curriculum.periodos_ideais,
        )
        return ContextoSemestre(
            matricula=profile.matricula,
            regra_matricula=REGRA_MATRICULA,
            prefixo_ingresso=prefixo,
            ano_ingresso=ano_ingresso,
            semestre_ingresso=semestre_ingresso,
            ano_alvo=ano_alvo,
            semestre_alvo=semestre_alvo,
            semestre_cronologico=semestre_cronologico,
            semestre_curricular=semestre_curricular,
            regra_semestre_curricular=REGRA_SEMESTRE_CURRICULAR,
            curso_codigo=profile.curso_codigo,
            ppc_id=curriculum.id,
            ppc_ano=curriculum.ano_versao,
            ppc_nome=curriculum.nome,
        )

    async def recommend(
        self,
        profile: UserProfile,
        *,
        ano: int | None = None,
        semestre: int | None = None,
    ) -> RecomendacaoAtual:
        curriculum = await self._get_curriculum(profile)
        ano_alvo, semestre_alvo = await self._target_period(ano, semestre)
        components = self._recommendation_components(
            await self._provider.list_curriculum_components(curriculum.id)
        )
        history = await self._provider.get_school_history(profile.matricula)
        if history is None:
            raise ResourceNotFoundError("Aluno", profile.matricula)
        equivalences = await self._provider.list_discipline_equivalences()
        context = self._build_context(
            profile,
            curriculum,
            ano_alvo,
            semestre_alvo,
            components,
            history,
            equivalences,
        )
        plan = await self._planos.list_by_user(profile.id)
        questionnaire = await self._questionarios.get_active(profile.id)
        offerings_page = await self._provider.list_class_offerings(
            limit=5000,
            ano=context.ano_alvo,
            semestre=context.semestre_alvo,
        )

        equivalent_codes = self._equivalent_codes_map(equivalences)
        latest_history = self._latest_attempts(history)
        candidates = tuple(
            component
            for component in components
            if component.tipo_componente == "DISCIPLINA_OBRIGATORIA"
            and component.disciplina_codigo
            and not self._is_approved(
                self._latest_equivalent_attempt(
                    component.disciplina_codigo,
                    latest_history,
                    equivalent_codes,
                )
            )
        )
        performance_history = self._history_by_equivalence(
            latest_history,
            equivalent_codes,
        )
        relevant_codes = {
            *(component.disciplina_codigo for component in candidates if component.disciplina_codigo),
            *performance_history.keys(),
        }
        statistics_codes = tuple(sorted({
            equivalent_code
            for code in relevant_codes
            for equivalent_code in self._equivalent_codes(code, equivalent_codes)
        }))
        statistics = await self._provider.get_discipline_statistics(
            statistics_codes,
            excluir_matricula=profile.matricula,
        )
        statistics_by_exact_code = {item.codigo: item for item in statistics}
        statistics_by_code = {
            code: statistic
            for code in relevant_codes
            if (statistic := self._aggregate_equivalent_statistics(
                code,
                statistics_by_exact_code,
                equivalent_codes,
            )) is not None
        }

        weights, questionnaire_index, questionnaire_completed = self._questionnaire_index(
            questionnaire
        )
        performance = self._performance_summary(
            performance_history,
            statistics_by_code,
        )
        weekly_limit = self._weekly_limit(
            questionnaire_index=questionnaire_index,
            questionnaire_completed=questionnaire_completed,
            recent_approval_rate=performance.taxa_aprovacao_recente,
        )
        high_risk_limit = self._high_risk_limit(performance)
        performance = ResumoDesempenho(
            tentativas_recentes=performance.tentativas_recentes,
            aprovacoes_recentes=performance.aprovacoes_recentes,
            taxa_aprovacao_recente=performance.taxa_aprovacao_recente,
            disciplinas_dificeis_cursadas=performance.disciplinas_dificeis_cursadas,
            disciplinas_dificeis_aprovadas=performance.disciplinas_dificeis_aprovadas,
            limite_disciplinas_alto_risco=high_risk_limit,
        )

        exact_offerings_by_code = self._offerings_by_code(
            offerings_page.items,
            profile.curso_codigo,
        )
        offerings_by_code = {
            component.disciplina_codigo: self._equivalent_offerings(
                component.disciplina_codigo,
                exact_offerings_by_code,
                equivalent_codes,
                profile.curso_codigo,
            )
            for component in candidates
            if component.disciplina_codigo
        }
        ordered_candidates = self._ordered_candidates(
            candidates,
            context.semestre_curricular,
            curriculum,
        )
        reference_semester = min(
            context.semestre_curricular,
            curriculum.periodos_ideais,
        )
        selected, not_selected = self._select_disciplines(
            ordered_candidates,
            offerings_by_code,
            latest_history,
            statistics_by_code,
            plan,
            weekly_limit,
            high_risk_limit,
            reference_semester,
            questionnaire_index,
            questionnaire_completed,
            performance,
            equivalent_codes,
        )

        # Enriquecimento informativo posterior à seleção. Estes dados não entram
        # em pontuação, limites, ordenação nem em qualquer regra do motor.
        dedication_codes = tuple(sorted({
            code
            for item in selected
            for code in (item.disciplina_codigo, item.oferta_disciplina_codigo)
        }))
        dedication_rows = await self._provider.get_discipline_extraclass_dedications(
            dedication_codes
        )
        dedication_by_code = {item.codigo: item for item in dedication_rows}
        selected = tuple(
            replace(
                item,
                dedicacao_extraclasse=self._dedication_indicator(
                    dedication_by_code.get(item.disciplina_codigo)
                    or dedication_by_code.get(item.oferta_disciplina_codigo)
                ),
            )
            for item in selected
        )

        total_hours = sum(item.carga_horaria for item in selected)
        weekly_hours = round(sum(item.horas_semanais for item in selected), 1)
        delayed_count = sum(item.atrasada for item in selected)
        advanced_count = sum(item.adiantada for item in selected)
        alerts: list[str] = []
        if not questionnaire_completed:
            alerts.append(
                "O questionário não está concluído; foi usada uma influência pessoal neutra."
            )
        if not plan:
            alerts.append(
                "O plano semanal está vazio; somente conflitos entre as ofertas foram verificados."
            )
        alerts.append(
            "Pré-requisitos formais ainda não estão cadastrados e não foram bloqueados automaticamente."
        )
        if any(component.tipo_componente == "BLOCO_DCG" for component in components):
            alerts.append(
                "Blocos genéricos de DCG não são escolhidos automaticamente nesta primeira versão."
            )

        message = (
            f"Escolhi {len(selected)} disciplinas para compor sua próxima etapa, "
            f"considerando o {context.semestre_curricular}º semestre curricular"
        )
        if delayed_count:
            message += f", incluindo {delayed_count} pendência(s) anterior(es)"
        if advanced_count:
            message += f" e {advanced_count} disciplina(s) adiantada(s) de baixo risco"
        message += "."

        return RecomendacaoAtual(
            titulo="O Salomão preparou este semestre para você",
            mensagem=message,
            contexto=context,
            carga_horaria_total=total_hours,
            horas_semanais=weekly_hours,
            limite_horas_semanais=weekly_limit,
            indice_questionario=questionnaire_index if questionnaire_completed else None,
            questionario_concluido=questionnaire_completed,
            plano_semanal_considerado=bool(plan),
            desempenho=performance,
            pesos_questionario=weights,
            disciplinas=selected,
            nao_selecionadas=not_selected,
            criterios=(
                "Priorizar obrigatórias do semestre curricular calculado pelo avanço no PPC.",
                "Recuperar pendências antigas sem concentrar várias disciplinas de alto risco.",
                "Adiantar disciplinas futuras somente quando forem de baixo risco e couberem na carga e no cronograma.",
                "Usar somente ofertas do período alvo que não conflitem com o plano semanal.",
                "Ajustar a carga pelo desempenho recente e pelo questionário concluído.",
                "Calcular a taxa de reprovação com tentativas de outros alunos.",
                "Reconhecer ofertas e históricos com códigos equivalentes de disciplina.",
            ),
            alertas=tuple(alerts),
        )

    @staticmethod
    def _dedication_indicator(
        dedication: DedicacaoExtraclasseDisciplina | None,
    ) -> IndicadorDedicacaoExtraclasse | None:
        if dedication is None or dedication.faixa_modal == "ATE_1H":
            return None
        if dedication.faixa_modal == "ENTRE_1_E_3H":
            return IndicadorDedicacaoExtraclasse(
                nivel="media",
                titulo="Tempo de dedicação média",
                descricao="Os alunos estimam um esforço médio de 2h semanais.",
                total_respostas=dedication.total_respostas,
            )
        if dedication.faixa_modal == "MAIS_DE_3H":
            return IndicadorDedicacaoExtraclasse(
                nivel="elevada",
                titulo="Tempo de dedicação elevado",
                descricao="Os alunos estimam mais de 3h de dedicação semanal.",
                total_respostas=dedication.total_respostas,
            )
        return None

    async def _get_curriculum(self, profile: UserProfile) -> Curriculo:
        if profile.ppc_id is None:
            raise ApplicationError(
                "Selecione o PPC no perfil antes de gerar a recomendação.",
                code="ppc_nao_selecionado",
            )
        curriculum = await self._provider.get_curriculum(profile.ppc_id)
        if curriculum is None or curriculum.curso_codigo != profile.curso_codigo:
            raise ResourceNotFoundError("PPC do perfil", profile.ppc_id)
        return curriculum

    async def _target_period(
        self,
        ano: int | None,
        semestre: int | None,
    ) -> tuple[int, int]:
        if (ano is None) != (semestre is None):
            raise ApplicationError(
                "Informe ano e semestre juntos.",
                code="periodo_incompleto",
            )
        if ano is not None and semestre is not None:
            if semestre not in (1, 2):
                raise ApplicationError(
                    "O semestre deve ser 1 ou 2.",
                    code="semestre_invalido",
                )
            return ano, semestre

        periods = await self._provider.list_academic_periods()
        if not periods:
            raise ApplicationError(
                "Não há período acadêmico com ofertas cadastrado.",
                code="periodo_sem_ofertas",
            )
        target = max(periods, key=lambda item: (item.ano, item.semestre))
        return target.ano, target.semestre

    @staticmethod
    def _parse_registration(registration: str) -> tuple[int, int, str]:
        prefix = registration[:5]
        if len(prefix) != 5 or not prefix.isdigit() or prefix[4] not in "12":
            raise ApplicationError(
                "A matrícula deve começar com quatro dígitos do ano e 1 ou 2 para o semestre.",
                code="matricula_periodo_invalido",
                details={"matricula": registration, "regra": REGRA_MATRICULA},
            )
        return int(prefix[:4]), int(prefix[4]), prefix

    @staticmethod
    def _semester_number(
        entry_year: int,
        entry_semester: int,
        target_year: int,
        target_semester: int,
    ) -> int:
        number = (target_year - entry_year) * 2 + (target_semester - entry_semester) + 1
        if number < 1:
            raise ApplicationError(
                "O período alvo é anterior ao ingresso indicado pela matrícula.",
                code="periodo_anterior_ingresso",
            )
        return number

    @classmethod
    def _effective_curricular_semester(
        cls,
        components: Iterable[ComponenteCurricular],
        latest_history: dict[str, ItemHistoricoEscolar],
        equivalent_codes: dict[str, frozenset[str]],
        chronological_semester: int,
        ideal_periods: int,
    ) -> int:
        upper_limit = max(1, min(chronological_semester, ideal_periods))
        required_by_semester: dict[int, list[ComponenteCurricular]] = {}
        for component in components:
            if (
                component.tipo_componente != "DISCIPLINA_OBRIGATORIA"
                or not component.disciplina_codigo
                or component.semestre_recomendado < 1
                or component.semestre_recomendado > upper_limit
            ):
                continue
            required_by_semester.setdefault(component.semestre_recomendado, []).append(component)

        for semester in sorted(required_by_semester):
            semester_components = required_by_semester[semester]
            total_hours = sum(max(0, item.carga_horaria) for item in semester_components)
            if total_hours <= 0:
                continue
            approved_hours = sum(
                max(0, item.carga_horaria)
                for item in semester_components
                if cls._is_approved(
                    cls._latest_equivalent_attempt(
                        item.disciplina_codigo,
                        latest_history,
                        equivalent_codes,
                    )
                )
            )
            if approved_hours / total_hours < LIMIAR_SEMESTRE_CONSOLIDADO:
                return semester

        return upper_limit

    @staticmethod
    def _normalized_text(value: str) -> str:
        return "".join(
            char
            for char in normalize("NFD", value.lower())
            if not combining(char)
        )

    @classmethod
    def _is_completion_work(cls, component: ComponenteCurricular) -> bool:
        name = cls._normalized_text(
            " ".join(
                part
                for part in (component.disciplina_nome, component.nome_no_ppc)
                if part
            )
        )
        words = set(name.replace("-", " ").split())
        return bool(words.intersection({"tcc", "tg"})) or any(
            term in name for term in TERMOS_TRABALHO_CONCLUSAO
        )

    @classmethod
    def _recommendation_components(
        cls,
        components: tuple[ComponenteCurricular, ...],
    ) -> tuple[ComponenteCurricular, ...]:
        return tuple(
            component
            for component in components
            if not cls._is_completion_work(component)
        )

    @classmethod
    def _is_approved(cls, item: ItemHistoricoEscolar | None) -> bool:
        if item is None:
            return False
        status = cls._normalized_text(item.situacao_final)
        return "aprovado" in status or "dispensado" in status

    @staticmethod
    def _history_order_key(item: ItemHistoricoEscolar) -> tuple[int, int, int]:
        return (
            item.ano,
            item.semestre,
            1 if item.fonte != "DIARIO_CLASSE" else 0,
        )

    @classmethod
    def _latest_attempts(
        cls,
        history: Iterable[ItemHistoricoEscolar],
    ) -> dict[str, ItemHistoricoEscolar]:
        latest: dict[str, ItemHistoricoEscolar] = {}
        for item in history:
            current = latest.get(item.disciplina_codigo)
            item_key = cls._history_order_key(item)
            current_key = cls._history_order_key(current) if current else (-1, -1, -1)
            if item_key >= current_key:
                latest[item.disciplina_codigo] = item
        return latest

    @staticmethod
    def _questionnaire_index(
        questionnaire: QuestionarioAtual | None,
    ) -> tuple[tuple[PesoQuestionarioAplicado, ...], float, bool]:
        if questionnaire is None:
            return (), 0.5, False

        completed = questionnaire.preenchimento.status == "CONCLUIDO"
        weighted_sum = 0.0
        total_weight = 0.0
        applied: list[PesoQuestionarioAplicado] = []
        scale_range = questionnaire.escala_maxima - questionnaire.escala_minima
        for section in questionnaire.secoes:
            for question in section.perguntas:
                weight = float(question.peso_recomendacao)
                if weight <= 0:
                    weight = PESOS_INICIAIS_QUESTIONARIO.get(question.codigo, 1.0)
                contribution = None
                if question.resposta is not None and scale_range > 0:
                    normalized_answer = (
                        question.resposta - questionnaire.escala_minima
                    ) / scale_range
                    contribution = round(normalized_answer * weight, 4)
                    weighted_sum += contribution
                    total_weight += weight
                applied.append(
                    PesoQuestionarioAplicado(
                        codigo=question.codigo,
                        texto=question.texto,
                        peso=weight,
                        resposta=question.resposta,
                        contribuicao_normalizada=contribution,
                    )
                )
        index = weighted_sum / total_weight if completed and total_weight else 0.5
        return tuple(applied), round(index, 4), completed

    @classmethod
    def _performance_summary(
        cls,
        latest_history: dict[str, ItemHistoricoEscolar],
        statistics: dict[str, EstatisticaDisciplina],
    ) -> ResumoDesempenho:
        periods = sorted(
            {(item.ano, item.semestre) for item in latest_history.values()},
            reverse=True,
        )[:2]
        recent = [
            item
            for item in latest_history.values()
            if (item.ano, item.semestre) in periods
        ]
        recent_approvals = sum(cls._is_approved(item) for item in recent)
        recent_rate = recent_approvals / len(recent) if recent else 0.5

        difficult = [
            item
            for code, item in latest_history.items()
            if statistics.get(code)
            and statistics[code].taxa_reprovacao >= TAXA_RISCO_ALTO
        ]
        difficult_approvals = sum(cls._is_approved(item) for item in difficult)
        return ResumoDesempenho(
            tentativas_recentes=len(recent),
            aprovacoes_recentes=recent_approvals,
            taxa_aprovacao_recente=round(recent_rate * 100, 2),
            disciplinas_dificeis_cursadas=len(difficult),
            disciplinas_dificeis_aprovadas=difficult_approvals,
            limite_disciplinas_alto_risco=1,
        )

    @staticmethod
    def _weekly_limit(
        *,
        questionnaire_index: float,
        questionnaire_completed: bool,
        recent_approval_rate: float,
    ) -> float:
        limit = LIMITE_BASE_HORAS_SEMANAIS
        if recent_approval_rate >= 80:
            limit += 4
        elif recent_approval_rate < 50:
            limit -= 4
        if questionnaire_completed:
            if questionnaire_index >= 0.70:
                limit += 4
            elif questionnaire_index < 0.40:
                limit -= 4
        return max(LIMITE_MINIMO_HORAS_SEMANAIS, min(LIMITE_MAXIMO_HORAS_SEMANAIS, limit))

    @staticmethod
    def _high_risk_limit(performance: ResumoDesempenho) -> int:
        if (
            performance.disciplinas_dificeis_cursadas >= 2
            and performance.disciplinas_dificeis_aprovadas
            / performance.disciplinas_dificeis_cursadas
            >= 0.65
        ):
            return 2
        return 1

    @staticmethod
    def _offerings_by_code(
        offerings: Iterable[OfertaTurma],
        student_course: str,
    ) -> dict[str, tuple[OfertaTurma, ...]]:
        grouped: dict[str, list[OfertaTurma]] = {}
        for offering in offerings:
            if not offering.horarios:
                continue
            grouped.setdefault(offering.disciplina_codigo, []).append(offering)
        return {
            code: tuple(
                sorted(
                    values,
                    key=lambda item: (
                        item.curso_codigo != student_course,
                        item.codigo_turma,
                        str(item.id),
                    ),
                )
            )
            for code, values in grouped.items()
        }

    @staticmethod
    def _equivalent_codes_map(
        equivalences: Iterable[DisciplinaEquivalencia],
    ) -> dict[str, frozenset[str]]:
        adjacency: dict[str, set[str]] = {}
        for equivalence in equivalences:
            first = equivalence.disciplina_codigo_a
            second = equivalence.disciplina_codigo_b
            adjacency.setdefault(first, set()).add(second)
            adjacency.setdefault(second, set()).add(first)
        return {
            code: frozenset((code, *neighbors))
            for code, neighbors in adjacency.items()
        }

    @staticmethod
    def _equivalent_codes(
        code: str,
        equivalent_codes: dict[str, frozenset[str]],
    ) -> frozenset[str]:
        return equivalent_codes.get(code, frozenset((code,)))

    @classmethod
    def _history_by_equivalence(
        cls,
        latest_history: dict[str, ItemHistoricoEscolar],
        equivalent_codes: dict[str, frozenset[str]],
    ) -> dict[str, ItemHistoricoEscolar]:
        grouped: dict[str, ItemHistoricoEscolar] = {}
        processed: set[str] = set()
        for code in latest_history:
            if code in processed:
                continue
            group = cls._equivalent_codes(code, equivalent_codes)
            canonical_code = min(group)
            latest = cls._latest_equivalent_attempt(
                code,
                latest_history,
                equivalent_codes,
            )
            if latest is not None:
                grouped[canonical_code] = latest
            processed.update(group)
        return grouped

    @classmethod
    def _latest_equivalent_attempt(
        cls,
        code: str,
        latest_history: dict[str, ItemHistoricoEscolar],
        equivalent_codes: dict[str, frozenset[str]],
    ) -> ItemHistoricoEscolar | None:
        attempts = (
            latest_history.get(equivalent_code)
            for equivalent_code in cls._equivalent_codes(code, equivalent_codes)
        )
        return max(
            (attempt for attempt in attempts if attempt is not None),
            key=cls._history_order_key,
            default=None,
        )

    @classmethod
    def _aggregate_equivalent_statistics(
        cls,
        code: str,
        statistics: dict[str, EstatisticaDisciplina],
        equivalent_codes: dict[str, frozenset[str]],
    ) -> EstatisticaDisciplina | None:
        items = [
            statistics[equivalent_code]
            for equivalent_code in cls._equivalent_codes(code, equivalent_codes)
            if equivalent_code in statistics
        ]
        if not items:
            return None
        total_attempts = sum(item.total_tentativas for item in items)
        total_failures = sum(item.total_reprovacoes for item in items)
        return EstatisticaDisciplina(
            codigo=code,
            total_tentativas=total_attempts,
            total_reprovacoes=total_failures,
            taxa_reprovacao=(
                round(total_failures * 100 / total_attempts, 2)
                if total_attempts
                else 0.0
            ),
        )

    @classmethod
    def _equivalent_offerings(
        cls,
        code: str,
        offerings_by_code: dict[str, tuple[OfertaTurma, ...]],
        equivalent_codes: dict[str, frozenset[str]],
        student_course: str,
    ) -> tuple[OfertaTurma, ...]:
        offerings = {
            offering.id: offering
            for equivalent_code in cls._equivalent_codes(code, equivalent_codes)
            for offering in offerings_by_code.get(equivalent_code, ())
        }
        return tuple(sorted(
            offerings.values(),
            key=lambda item: (
                item.disciplina_codigo != code,
                item.curso_codigo != student_course,
                item.codigo_turma,
                str(item.id),
            ),
        ))

    @staticmethod
    def _ordered_candidates(
        candidates: tuple[ComponenteCurricular, ...],
        current_semester: int,
        curriculum: Curriculo,
    ) -> tuple[ComponenteCurricular, ...]:
        reference_semester = min(current_semester, curriculum.periodos_ideais)
        current = sorted(
            (
                item
                for item in candidates
                if item.semestre_recomendado == reference_semester
            ),
            key=lambda item: item.ordem_semestre,
        )
        delayed = sorted(
            (
                item
                for item in candidates
                if item.semestre_recomendado < reference_semester
            ),
            key=lambda item: (item.semestre_recomendado, item.ordem_semestre),
        )
        future = sorted(
            (
                item
                for item in candidates
                if item.semestre_recomendado > reference_semester
            ),
            key=lambda item: (item.semestre_recomendado, item.ordem_semestre),
        )
        return tuple((*current, *delayed, *future))

    def _select_disciplines(
        self,
        candidates: tuple[ComponenteCurricular, ...],
        offerings_by_code: dict[str, tuple[OfertaTurma, ...]],
        latest_history: dict[str, ItemHistoricoEscolar],
        statistics: dict[str, EstatisticaDisciplina],
        plan: tuple[PlanoSemanaItem, ...],
        weekly_limit: float,
        high_risk_limit: int,
        reference_semester: int,
        questionnaire_index: float,
        questionnaire_completed: bool,
        performance: ResumoDesempenho,
        equivalent_codes: dict[str, frozenset[str]],
    ) -> tuple[tuple[DisciplinaRecomendada, ...], tuple[DisciplinaNaoSelecionada, ...]]:
        selected: list[DisciplinaRecomendada] = []
        not_selected: list[DisciplinaNaoSelecionada] = []
        occupied = [
            (item.dia_semana, item.hora_inicio, item.hora_fim)
            for item in plan
        ]
        selected_hours = 0.0
        high_risk_count = 0

        for component in candidates:
            code = component.disciplina_codigo
            if code is None:
                continue
            name = component.disciplina_nome or component.nome_no_ppc
            statistic = statistics.get(code)
            risk = self._risk_level(statistic)
            advanced = component.semestre_recomendado > reference_semester
            if advanced and risk != "baixo":
                not_selected.append(
                    DisciplinaNaoSelecionada(
                        disciplina_codigo=code,
                        disciplina_nome=name,
                        semestre_recomendado=component.semestre_recomendado,
                        motivo_codigo="DISCIPLINA_FUTURA_RISCO_NAO_BAIXO",
                        motivo=(
                            "Disciplinas futuras só podem ser adiantadas quando "
                            "possuem taxa de reprovação conhecida e risco baixo."
                        ),
                    )
                )
                continue

            offerings = offerings_by_code.get(code, ())
            if not offerings:
                not_selected.append(
                    DisciplinaNaoSelecionada(
                        disciplina_codigo=code,
                        disciplina_nome=name,
                        semestre_recomendado=component.semestre_recomendado,
                        motivo_codigo="SEM_OFERTA_COM_HORARIO",
                        motivo="Não foi encontrada oferta com horários para o período alvo.",
                    )
                )
                continue

            available = next(
                (
                    offering
                    for offering in offerings
                    if not self._has_conflict(offering, occupied)
                ),
                None,
            )
            if available is None:
                not_selected.append(
                    DisciplinaNaoSelecionada(
                        disciplina_codigo=code,
                        disciplina_nome=name,
                        semestre_recomendado=component.semestre_recomendado,
                        motivo_codigo="CONFLITO_HORARIO",
                        motivo="Todas as ofertas conflitam com o plano ou com outra disciplina selecionada.",
                    )
                )
                continue

            weekly_hours = self._offering_weekly_hours(available)
            if selected_hours + weekly_hours > weekly_limit:
                not_selected.append(
                    DisciplinaNaoSelecionada(
                        disciplina_codigo=code,
                        disciplina_nome=name,
                        semestre_recomendado=component.semestre_recomendado,
                        motivo_codigo="LIMITE_CARGA",
                        motivo=f"Ultrapassaria o limite calculado de {weekly_limit:g} horas semanais.",
                    )
                )
                continue

            if risk == "alto" and high_risk_count >= high_risk_limit:
                not_selected.append(
                    DisciplinaNaoSelecionada(
                        disciplina_codigo=code,
                        disciplina_nome=name,
                        semestre_recomendado=component.semestre_recomendado,
                        motivo_codigo="LIMITE_ALTO_RISCO",
                        motivo="Outra disciplina de alto risco já foi incluída nesta combinação.",
                    )
                )
                continue

            previous = self._latest_equivalent_attempt(
                code,
                latest_history,
                equivalent_codes,
            )
            delayed = component.semestre_recomendado < reference_semester
            motives = self._discipline_reasons(
                component,
                delayed,
                advanced,
                previous,
                statistic,
                performance,
                questionnaire_completed,
                available.disciplina_codigo,
            )
            alerts: list[str] = []
            if previous is not None and not self._is_approved(previous):
                alerts.append(
                    f"Última tentativa: {previous.situacao_final} em {previous.ano}/{previous.semestre}."
                )
            if risk == "alto":
                alerts.append("É o principal ponto de atenção da combinação atual.")

            score = self._discipline_score(
                component=component,
                delayed=delayed,
                advanced=advanced,
                previous=previous,
                statistic=statistic,
                performance=performance,
                questionnaire_index=questionnaire_index,
                questionnaire_completed=questionnaire_completed,
                current_semester=reference_semester,
            )
            recommendation = DisciplinaRecomendada(
                componente_id=component.id,
                disciplina_codigo=code,
                oferta_disciplina_codigo=available.disciplina_codigo,
                equivalencia_utilizada=available.disciplina_codigo != code,
                disciplina_nome=name,
                semestre_recomendado=component.semestre_recomendado,
                atrasada=delayed,
                adiantada=advanced,
                oferta_turma_id=available.id,
                codigo_turma=available.codigo_turma,
                carga_horaria=component.carga_horaria,
                horas_semanais=weekly_hours,
                taxa_reprovacao=statistic.taxa_reprovacao if statistic else None,
                amostra_taxa_reprovacao=statistic.total_tentativas if statistic else 0,
                nivel_risco=risk,
                pontuacao=score,
                justificativa=self._discipline_justification(
                    component=component,
                    delayed=delayed,
                    advanced=advanced,
                    previous=previous,
                    risk=risk,
                    performance=performance,
                    questionnaire_index=questionnaire_index,
                    questionnaire_completed=questionnaire_completed,
                    plan_considered=bool(plan),
                ),
                motivos=motives,
                alertas=tuple(alerts),
                horarios=tuple(
                    HorarioRecomendado(
                        id=schedule.id,
                        dia_semana=schedule.dia_semana,
                        dia_nome=schedule.dia_nome,
                        hora_inicio=schedule.hora_inicio,
                        hora_fim=schedule.hora_fim,
                        sala=schedule.sala,
                    )
                    for schedule in available.horarios
                ),
            )
            selected.append(recommendation)
            selected_hours += weekly_hours
            if risk == "alto":
                high_risk_count += 1
            occupied.extend(
                (schedule.dia_semana, schedule.hora_inicio, schedule.hora_fim)
                for schedule in available.horarios
            )

        return tuple(selected), tuple(not_selected)

    @staticmethod
    def _has_conflict(
        offering: OfertaTurma,
        occupied: Iterable[tuple[int, time, time]],
    ) -> bool:
        occupied_items = tuple(occupied)
        return any(
            schedule.dia_semana == day
            and schedule.hora_inicio < end
            and start < schedule.hora_fim
            for schedule in offering.horarios
            for day, start, end in occupied_items
        )

    @staticmethod
    def _minutes(value: time) -> int:
        return value.hour * 60 + value.minute

    @classmethod
    def _offering_weekly_hours(cls, offering: OfertaTurma) -> float:
        minutes = sum(
            cls._minutes(item.hora_fim) - cls._minutes(item.hora_inicio)
            for item in offering.horarios
        )
        return round(minutes / 60, 1)

    @staticmethod
    def _risk_level(statistic: EstatisticaDisciplina | None) -> str:
        if statistic is None or statistic.total_tentativas == 0:
            return "desconhecido"
        if statistic.taxa_reprovacao >= TAXA_RISCO_ALTO:
            return "alto"
        if statistic.taxa_reprovacao >= TAXA_RISCO_MEDIO:
            return "medio"
        return "baixo"

    @classmethod
    def _discipline_reasons(
        cls,
        component: ComponenteCurricular,
        delayed: bool,
        advanced: bool,
        previous: ItemHistoricoEscolar | None,
        statistic: EstatisticaDisciplina | None,
        performance: ResumoDesempenho,
        questionnaire_completed: bool,
        offering_code: str,
    ) -> tuple[str, ...]:
        if delayed:
            curriculum_reason = (
                f"Pendência do {component.semestre_recomendado}º semestre."
            )
        elif advanced:
            curriculum_reason = (
                f"Disciplina do {component.semestre_recomendado}º semestre adiantada "
                "por possuir baixo risco e ser compatível com a carga e o cronograma."
            )
        else:
            curriculum_reason = (
                f"Prevista no PPC para o {component.semestre_recomendado}º semestre."
            )
        reasons = [curriculum_reason]
        if offering_code != component.disciplina_codigo:
            reasons.append(
                f"A oferta {offering_code} foi reconhecida como equivalente a "
                f"{component.disciplina_codigo} do PPC."
            )
        if previous is not None and not cls._is_approved(previous):
            reasons.append("A recuperação foi priorizada sem repetir várias matérias difíceis juntas.")
        if statistic is not None:
            reasons.append(
                f"Taxa de reprovação de {statistic.taxa_reprovacao:g}% em "
                f"{statistic.total_tentativas} tentativas de outros alunos."
            )
        if performance.taxa_aprovacao_recente >= 80:
            reasons.append("O desempenho recente permitiu uma carga semanal maior.")
        if questionnaire_completed:
            reasons.append("As respostas do questionário participaram do limite de carga.")
        return tuple(reasons)

    @classmethod
    def _discipline_justification(
        cls,
        *,
        component: ComponenteCurricular,
        delayed: bool,
        advanced: bool,
        previous: ItemHistoricoEscolar | None,
        risk: str,
        performance: ResumoDesempenho,
        questionnaire_index: float,
        questionnaire_completed: bool,
        plan_considered: bool,
    ) -> str:
        good_recent_performance = (
            performance.tentativas_recentes > 0
            and performance.taxa_aprovacao_recente >= 80
        )
        handled_difficult_disciplines = (
            performance.disciplinas_dificeis_aprovadas > 0
        )
        favorable_questionnaire = (
            questionnaire_completed and questionnaire_index >= 0.65
        )

        if delayed:
            if previous is not None and not cls._is_approved(previous):
                opening = (
                    "Esta disciplina continua pendente após uma tentativa anterior e "
                    "foi priorizada para evitar que o atraso aumente."
                )
            else:
                opening = (
                    f"Esta disciplina está pendente desde o "
                    f"{component.semestre_recomendado}º semestre e foi priorizada "
                    "para ajudar a regularizar sua trajetória."
                )

            if good_recent_performance:
                support = (
                    "Seu bom desempenho recente indica margem para incluí-la nesta "
                    "combinação."
                )
            elif risk == "alto" and handled_difficult_disciplines:
                support = (
                    "Seu histórico mostra aprovações em disciplinas difíceis, e o "
                    "plano respeita o limite de matérias de alto risco."
                )
            elif risk == "baixo":
                support = (
                    "O baixo risco de reprovação e a carga compatível tornam sua "
                    "inclusão viável."
                )
            else:
                support = (
                    "Ela cabe no limite de carga e foi combinada sem ultrapassar o "
                    "limite de disciplinas de alto risco."
                )
            return f"{opening} {support}"

        if advanced:
            opening = (
                "Esta disciplina de um semestre futuro foi antecipada porque possui "
                "baixo risco de reprovação e cabe na carga semanal calculada."
            )
            support = (
                "Os horários também são compatíveis com o seu plano semanal."
                if plan_considered
                else "Ela não conflita com as outras disciplinas selecionadas."
            )
            return f"{opening} {support}"

        opening = (
            "Esta disciplina acompanha o semestre curricular identificado pelo seu "
            "avanço na grade."
        )
        if risk == "alto":
            if good_recent_performance or handled_difficult_disciplines:
                support = (
                    "Apesar do risco elevado, seu desempenho anterior indica que ela "
                    "é viável nesta combinação, respeitando o limite de matérias "
                    "difíceis."
                )
            else:
                support = (
                    "Ela foi mantida como principal ponto de atenção, sem ultrapassar "
                    "o limite de disciplinas de alto risco."
                )
        elif good_recent_performance:
            support = (
                "Seu bom desempenho recente e a carga compatível favorecem sua "
                "inclusão neste semestre."
            )
        elif favorable_questionnaire:
            support = (
                "Suas respostas indicam disponibilidade compatível com a carga "
                "necessária para cursá-la."
            )
        elif risk == "baixo":
            support = (
                "O baixo risco de reprovação ajuda a manter a combinação equilibrada."
            )
        elif plan_considered:
            support = (
                "A oferta cabe na carga calculada e não conflita com os horários "
                "informados no seu plano."
            )
        else:
            support = (
                "A oferta cabe no limite semanal e não conflita com as outras "
                "disciplinas selecionadas."
            )
        return f"{opening} {support}"

    @classmethod
    def _discipline_score(
        cls,
        *,
        component: ComponenteCurricular,
        delayed: bool,
        advanced: bool,
        previous: ItemHistoricoEscolar | None,
        statistic: EstatisticaDisciplina | None,
        performance: ResumoDesempenho,
        questionnaire_index: float,
        questionnaire_completed: bool,
        current_semester: int,
    ) -> float:
        score = 70.0
        if delayed:
            score += min(20, (current_semester - component.semestre_recomendado) * 4)
        elif not advanced:
            score += 20
        if previous is not None and not cls._is_approved(previous):
            score += 5
        if statistic is not None:
            score -= statistic.taxa_reprovacao * 0.35
        score += (performance.taxa_aprovacao_recente - 50) * 0.15
        if questionnaire_completed:
            score += (questionnaire_index - 0.5) * 10
        return round(max(0, min(100, score)), 1)
