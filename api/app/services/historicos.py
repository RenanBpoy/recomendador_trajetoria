from __future__ import annotations

import hashlib
import re
import unicodedata
from difflib import SequenceMatcher

from app.core.errors import ApplicationError, ResourceNotFoundError
from app.domain.entities import (
    CandidatoEquivalencia,
    ComponenteCurricular,
    CorrespondenciaProposta,
    EquivalenciaManual,
    ImportacaoHistorico,
    ItemHistoricoDocumento,
    UserProfile,
)
from app.domain.ports import (
    AcademicDataProvider,
    EquivalenciaManualRepository,
    HistoricoDocumentoProvider,
    HistoricoImportacaoRepository,
)

MAX_PDF_SIZE = 10 * 1024 * 1024
AUTO_MATCH_THRESHOLD = 0.86
SUGGESTION_THRESHOLD = 0.70
MINIMUM_BEST_MARGIN = 0.04


def normalize_discipline_name(value: str) -> str:
    value = "".join(
        char
        for char in unicodedata.normalize("NFD", value)
        if not unicodedata.combining(char)
    ).upper()
    value = re.sub(r"[^A-Z0-9]+", " ", value)
    tokens = value.split()
    if len(tokens) > 1 and tokens[-1] in {"A", "B", "C"}:
        tokens.pop()
    return " ".join(tokens)


def discipline_name_similarity(left: str, right: str) -> float:
    left_normalized = normalize_discipline_name(left)
    right_normalized = normalize_discipline_name(right)
    if not left_normalized or not right_normalized:
        return 0.0
    if left_normalized == right_normalized:
        return 1.0

    left_tokens = left_normalized.split()
    right_tokens = right_normalized.split()
    left_set = set(left_tokens)
    right_set = set(right_tokens)
    token_score = (2 * len(left_set & right_set)) / (len(left_set) + len(right_set))
    sequence_score = SequenceMatcher(None, left_normalized, right_normalized).ratio()
    return max(token_score, sequence_score)


def _distinctive_tokens_compatible(left: str, right: str) -> bool:
    markers = {"I", "II", "III", "IV", "V", "VI", "1", "2", "3", "4", "5", "6"}
    left_markers = set(normalize_discipline_name(left).split()) & markers
    right_markers = set(normalize_discipline_name(right).split()) & markers
    return not (left_markers and right_markers and left_markers != right_markers)


def _workload_compatible(item: ItemHistoricoDocumento, component: ComponenteCurricular) -> bool:
    tolerance = max(15, round(component.carga_horaria * 0.20))
    return abs(item.carga_horaria - component.carga_horaria) <= tolerance


def propose_match(
    item: ItemHistoricoDocumento,
    components: tuple[ComponenteCurricular, ...],
) -> CorrespondenciaProposta | None:
    candidates = tuple(
        component
        for component in components
        if component.disciplina_codigo and component.tipo_componente == "DISCIPLINA_OBRIGATORIA"
    )
    source_code = item.codigo.strip().upper()
    for component in candidates:
        if component.disciplina_codigo and component.disciplina_codigo.strip().upper() == source_code:
            return CorrespondenciaProposta(
                item_indice=-1,
                ppc_id=component.ppc_id,
                ppc_componente_id=component.id,
                metodo="CODIGO_EXATO",
                confianca=1.0,
                status="CONFIRMADA",
            )

    source_name = normalize_discipline_name(item.nome)
    exact_name = [
        component
        for component in candidates
        if _workload_compatible(item, component)
        and normalize_discipline_name(component.disciplina_nome or component.nome_no_ppc)
        == source_name
    ]
    if len(exact_name) == 1:
        component = exact_name[0]
        return CorrespondenciaProposta(
            item_indice=-1,
            ppc_id=component.ppc_id,
            ppc_componente_id=component.id,
            metodo="NOME_NORMALIZADO",
            confianca=0.99,
            status="CONFIRMADA",
        )

    scored = sorted(
        (
            (
                discipline_name_similarity(
                    item.nome, component.disciplina_nome or component.nome_no_ppc
                ),
                component,
            )
            for component in candidates
            if _workload_compatible(item, component)
            and _distinctive_tokens_compatible(
                item.nome, component.disciplina_nome or component.nome_no_ppc
            )
        ),
        key=lambda entry: entry[0],
        reverse=True,
    )
    if not scored or scored[0][0] < SUGGESTION_THRESHOLD:
        return None

    best_score, component = scored[0]
    second_score = scored[1][0] if len(scored) > 1 else 0.0
    automatic = (
        best_score >= AUTO_MATCH_THRESHOLD
        and best_score - second_score >= MINIMUM_BEST_MARGIN
    )
    return CorrespondenciaProposta(
        item_indice=-1,
        ppc_id=component.ppc_id,
        ppc_componente_id=component.id,
        metodo="NOME_SEMELHANTE",
        confianca=round(best_score, 4),
        status="CONFIRMADA" if automatic else "SUGERIDA",
    )


class ImportacaoHistoricoService:
    def __init__(
        self,
        *,
        academic: AcademicDataProvider,
        documents: HistoricoDocumentoProvider,
        imports: HistoricoImportacaoRepository,
    ) -> None:
        self._academic = academic
        self._documents = documents
        self._imports = imports

    async def import_pdf(
        self,
        *,
        profile: UserProfile,
        filename: str,
        content: bytes,
    ) -> ImportacaoHistorico:
        if not filename.lower().endswith(".pdf"):
            self._invalid("Envie o histórico escolar no formato PDF.")
        if not content:
            self._invalid("O arquivo enviado está vazio.")
        if len(content) > MAX_PDF_SIZE:
            self._invalid("O PDF deve ter no máximo 10 MB.")

        document = self._documents.read(content)
        if document.matricula != profile.matricula:
            self._invalid(
                "A matrícula do histórico não corresponde ao usuário logado.",
                details={
                    "matricula_documento": document.matricula,
                    "matricula_usuario": profile.matricula,
                },
            )
        if document.curso_codigo != profile.curso_codigo:
            self._invalid(
                "O curso do histórico não corresponde ao curso cadastrado no perfil.",
                details={
                    "curso_documento": document.curso_codigo,
                    "curso_usuario": profile.curso_codigo,
                },
            )

        curricula = await self._academic.list_curricula(profile.curso_codigo)
        if not curricula:
            raise ResourceNotFoundError("PPC do curso", profile.curso_codigo)
        reference = next((item for item in curricula if item.id == profile.ppc_id), None)
        if reference is None:
            reference = next(
                (item for item in curricula if item.ano_versao == document.ppc_ano),
                None,
            )
        if reference is None:
            reference = next((item for item in curricula if item.curriculo_corrente), curricula[0])

        matches: list[CorrespondenciaProposta] = []
        for curriculum in curricula:
            components = await self._academic.list_curriculum_components(curriculum.id)
            for index, item in enumerate(document.itens):
                match = propose_match(item, components)
                if match is not None:
                    matches.append(
                        CorrespondenciaProposta(
                            item_indice=index,
                            ppc_id=match.ppc_id,
                            ppc_componente_id=match.ppc_componente_id,
                            metodo=match.metodo,
                            confianca=match.confianca,
                            status=match.status,
                        )
                    )

        return await self._imports.replace_active(
            usuario_id=profile.id,
            nome_arquivo=filename,
            hash_arquivo=hashlib.sha256(content).hexdigest(),
            documento=document,
            ppc_referencia_id=reference.id,
            correspondencias=tuple(matches),
        )

    async def get_active(self, user_id) -> ImportacaoHistorico | None:
        return await self._imports.get_active(user_id)

    async def review(
        self, *, user_id, correspondence_id: int, action: str
    ) -> ImportacaoHistorico:
        if action not in {"confirmar", "rejeitar"}:
            self._invalid("A ação deve ser 'confirmar' ou 'rejeitar'.")
        result = await self._imports.review_correspondence(
            usuario_id=user_id,
            correspondencia_id=correspondence_id,
            action=action,
        )
        if result is None:
            raise ResourceNotFoundError("Correspondência do histórico", correspondence_id)
        return result

    @staticmethod
    def _invalid(message: str, *, details=None) -> None:
        raise ApplicationError(
            message,
            code="historico_importacao_invalida",
            status_code=422,
            details=details,
        )


def _is_completed_status(value: str) -> bool:
    normalized = normalize_discipline_name(value)
    return any(
        marker in normalized
        for marker in ("APROVADO", "DISPENSADO", "DISPENSA", "APROVEITAMENTO")
    )


class EquivalenciaManualService:
    def __init__(
        self,
        *,
        academic: AcademicDataProvider,
        equivalences: EquivalenciaManualRepository,
    ) -> None:
        self._academic = academic
        self._equivalences = equivalences

    async def list_mappings(
        self, *, profile: UserProfile
    ) -> tuple[EquivalenciaManual, ...]:
        ppc_id = self._require_ppc(profile)
        return await self._equivalences.list_mappings(
            usuario_id=profile.id, ppc_id=ppc_id
        )

    async def list_candidates(
        self, *, profile: UserProfile, component_id: int
    ) -> tuple[CandidatoEquivalencia, ...]:
        component = await self._get_component(profile, component_id)
        candidates = await self._equivalences.list_candidates(
            usuario_id=profile.id,
            ppc_id=component.ppc_id,
        )
        evaluated = tuple(
            self._evaluate_candidate(candidate, component) for candidate in candidates
        )
        return tuple(
            sorted(
                evaluated,
                key=lambda item: (
                    not item.selecionavel,
                    -(item.similaridade_nome or 0.0),
                    -item.ano,
                    -item.semestre,
                    item.nome_original,
                ),
            )
        )

    async def save(
        self,
        *,
        profile: UserProfile,
        component_id: int,
        slot_order: int,
        history_item_id: int,
    ) -> EquivalenciaManual:
        component = await self._get_component(profile, component_id)
        self._validate_slot(component, slot_order)

        mappings = await self._equivalences.list_mappings(
            usuario_id=profile.id, ppc_id=component.ppc_id
        )
        current = next(
            (
                mapping
                for mapping in mappings
                if mapping.ppc_componente_id == component_id
                and mapping.slot_ordem == slot_order
            ),
            None,
        )
        if current and current.historico_item_id == history_item_id:
            return current

        candidates = await self.list_candidates(
            profile=profile, component_id=component_id
        )
        candidate = next(
            (item for item in candidates if item.id == history_item_id), None
        )
        if candidate is None:
            self._invalid(
                "A disciplina não está disponível entre os itens não mapeados do histórico."
            )
        if not candidate.selecionavel:
            self._invalid(
                candidate.motivo_indisponibilidade
                or "A disciplina escolhida não pode ser usada nesta vaga."
            )

        return await self._equivalences.save(
            usuario_id=profile.id,
            ppc_id=component.ppc_id,
            ppc_componente_id=component_id,
            slot_ordem=slot_order,
            historico_item_id=history_item_id,
        )

    async def remove(
        self,
        *,
        profile: UserProfile,
        component_id: int,
        slot_order: int,
    ) -> None:
        component = await self._get_component(profile, component_id)
        self._validate_slot(component, slot_order)
        removed = await self._equivalences.delete(
            usuario_id=profile.id,
            ppc_id=component.ppc_id,
            ppc_componente_id=component_id,
            slot_ordem=slot_order,
        )
        if not removed:
            raise ResourceNotFoundError(
                "Equivalência manual",
                f"{component_id}:{slot_order}",
            )

    async def _get_component(
        self, profile: UserProfile, component_id: int
    ) -> ComponenteCurricular:
        ppc_id = self._require_ppc(profile)
        components = await self._academic.list_curriculum_components(ppc_id)
        component = next((item for item in components if item.id == component_id), None)
        if component is None:
            raise ResourceNotFoundError("Componente do PPC", component_id)
        return component

    def _evaluate_candidate(
        self,
        candidate: CandidatoEquivalencia,
        component: ComponenteCurricular,
    ) -> CandidatoEquivalencia:
        reason = None
        if candidate.em_uso:
            reason = "Esta disciplina já foi usada em outra vaga da grade."
        elif not _is_completed_status(candidate.situacao):
            reason = "Somente disciplinas concluídas ou dispensadas podem ser vinculadas."
        elif component.tipo_componente == "BLOCO_DCG" and candidate.carga_horaria < 60:
            reason = "Esta disciplina tem menos de 60 horas e não preenche uma vaga de DCG."

        similarity = None
        if component.tipo_componente == "DISCIPLINA_OBRIGATORIA":
            similarity = round(
                discipline_name_similarity(
                    candidate.nome_original,
                    component.disciplina_nome or component.nome_no_ppc,
                ),
                4,
            )
        return CandidatoEquivalencia(
            id=candidate.id,
            codigo_original=candidate.codigo_original,
            nome_original=candidate.nome_original,
            carga_horaria=candidate.carga_horaria,
            ano=candidate.ano,
            semestre=candidate.semestre,
            situacao=candidate.situacao,
            media=candidate.media,
            selecionavel=reason is None,
            motivo_indisponibilidade=reason,
            similaridade_nome=similarity,
            em_uso=candidate.em_uso,
            componente_em_uso_id=candidate.componente_em_uso_id,
            slot_em_uso=candidate.slot_em_uso,
        )

    @staticmethod
    def _require_ppc(profile: UserProfile) -> int:
        if profile.ppc_id is None:
            EquivalenciaManualService._invalid(
                "Escolha um PPC no perfil antes de organizar as equivalências."
            )
        return profile.ppc_id

    @staticmethod
    def _validate_slot(component: ComponenteCurricular, slot_order: int) -> None:
        max_slots = (
            max(1, (component.carga_horaria + 59) // 60)
            if component.tipo_componente == "BLOCO_DCG"
            else 1
        )
        if slot_order < 1 or slot_order > max_slots:
            EquivalenciaManualService._invalid(
                f"A vaga deve estar entre 1 e {max_slots} para este componente."
            )

    @staticmethod
    def _invalid(message: str) -> None:
        raise ApplicationError(
            message,
            code="equivalencia_manual_invalida",
            status_code=422,
        )
