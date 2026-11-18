"""Official academic data for the existing recommendation engine."""
from collections import Counter
from datetime import time
from urllib.parse import quote, urlencode
from uuid import NAMESPACE_URL, UUID, uuid5

from app.core.errors import DataSourceUnavailableError
from app.domain.entities import (
    ComponenteCurricular, Curriculo, DisciplinaEquivalencia, EstatisticaDisciplina,
    HorarioOfertaTurma, ItemHistoricoEscolar, OfertaTurma, Page, PeriodoAcademico,
)
from app.services.ufsm_offerings import (
    OFFER_CACHE_TTL, cached_academic_data, cached_offering_courses, normalize_offering,
)

STATISTICS_CACHE_TTL = 6 * 60 * 60


def simple_equivalences(rules, components, ppc_id):
    ids = {row["id"]: row.get("disciplina_codigo") for row in components}
    codes = set(ids.values())
    pairs = set()
    for rule in rules:
        target = rule.get("disciplinaCodigo")
        groups = rule.get("grupos") or []
        if not target or not groups:
            continue
        for group in groups:
            subjects = group.get("disciplinas") or []
            source = subjects[0].get("codigo") if len(subjects) == 1 else None
            if not source or source == target:
                continue
            if (
                (rule.get("ppcId") == ppc_id and ids.get(rule.get("componenteId")) == target)
                or (rule.get("ppcId") != ppc_id and len(groups) == 1 and source in codes)
            ):
                pairs.add(tuple(sorted((target, source))))
    return tuple(DisciplinaEquivalencia(a, b, "UFSM_OFICIAL", 1.0) for a, b in sorted(pairs))


def statistic_for(code, data, history):
    attempts = data.get("totalTentativas")
    by_grade = data.get("reprovacoesPorNota")
    by_attendance = data.get("reprovacoesPorFrequencia")
    if any(type(n) is not int or n < 0 for n in (attempts, by_grade, by_attendance)):
        raise DataSourceUnavailableError("A UFSM retornou estatísticas acadêmicas inválidas.")
    own = Counter(
        item.get("grupo_situacao")
        for item in history if item["disciplina_codigo"] == code
        and item.get("grupo_situacao") not in {"DISPENSA", "APROVEITAMENTO"}
    )
    total = max(0, attempts - sum(own.values()))
    failures = max(0, by_grade + by_attendance - own["REPROVADO_NOTA"] - own["REPROVADO_FREQUENCIA"])
    failures = min(total, failures)
    return EstatisticaDisciplina(code, total, failures, round(failures * 100 / total, 2) if total else 0.0)


class UfsmRecommendationProvider:
    def __init__(self, auth, token, snapshot, profile, legacy):
        self.auth = auth
        self.token = token
        self.snapshot = snapshot
        self.profile = profile
        self.legacy = legacy

    async def get_curriculum(self, ppc_id):
        row = self.snapshot["curriculo"]
        if row["id"] != ppc_id:
            return None
        try:
            year = int(row["ano_versao"])
            duration = int(row["periodos_ideais"])
            if duration <= 0:
                raise ValueError
        except (KeyError, ValueError, TypeError):
            raise DataSourceUnavailableError("O PPC da UFSM não informa ano e duração válidos.") from None
        return Curriculo(
            ppc_id, self.profile.curso_codigo, year, row.get("nome") or str(year),
            bool(row.get("curriculo_corrente")), duration,
            row.get("carga_horaria_total") or 0, row.get("carga_horaria_extensao") or 0,
            "UFSM",
        )

    async def list_curriculum_components(self, ppc_id):
        return tuple(ComponenteCurricular(
            row["id"], ppc_id, row.get("disciplina_codigo"), row["semestre_recomendado"],
            row.get("ordem_semestre") or 0, row["tipo_componente"], row.get("nome_no_ppc") or "",
            None, row.get("carga_horaria") or 0,
        ) for row in self.snapshot["componentes"] if row.get("semestre_recomendado")
            and type(row.get("id")) is int)

    async def list_discipline_equivalences(self):
        return simple_equivalences(self.snapshot.get("equivalencias", []),
                                   self.snapshot["componentes"], self.profile.ppc_id)

    async def get_school_history(self, matricula):
        if matricula != self.profile.matricula:
            return None
        return tuple(ItemHistoricoEscolar(
            matricula, row["disciplina_codigo"], row.get("disciplina") or row["disciplina_codigo"],
            None, row["ano"], row.get("semestre") or 0, row.get("codigo_turma") or "",
            row.get("media_final"), row.get("faltas_total") or 0, row.get("situacao_final") or "",
            fonte="UFSM", cumprido_oficial=row.get("cumprido"),
        ) for row in self.snapshot["historico"] if row.get("ano"))

    async def list_academic_periods(self):
        rows = await cached_academic_data(self.auth, self.token, "/periodos?" + urlencode({
            "cursoCodigo": self.profile.curso_codigo,
        }))
        return tuple(PeriodoAcademico(row["ano"], row["semestre"]) for row in rows
                     if type(row.get("ano")) is int and row.get("semestre") in (1, 2))

    async def get_discipline_statistics(self, codigos, *, excluir_matricula=None):
        history = self.snapshot["historico"] if excluir_matricula == self.profile.matricula else ()
        result = []
        for code in codigos:
            data = await cached_academic_data(
                self.auth, self.token, f"/disciplinas/{quote(code, safe='')}/estatisticas",
                ttl=STATISTICS_CACHE_TTL, object_result=True, allow_missing=True,
            )
            if data is None:
                # Alguns códigos do histórico (ex.: atividades de extensão)
                # não constam no catálogo de estatísticas da DTI.
                continue
            result.append(statistic_for(code, data.get("resultados") or {}, history))
        return tuple(result)

    async def get_discipline_extraclass_dedications(self, codigos):
        return await self.legacy.get_discipline_extraclass_dedications(codigos)

    async def list_recommendation_offerings(self, *, codes, ano, semestre):
        if not codes:
            return Page(())
        own = self.profile.curso_codigo
        # A UFSM exige o curso na consulta. O catálogo local fornece apenas pistas:
        # somente as turmas que a UFSM confirmar para o período entram no motor.
        hints = set()
        cursor = None
        while True:
            old = await self.legacy.list_class_offerings(limit=500, cursor=cursor)
            hints.update(row.curso_codigo for row in old.items if row.disciplina_codigo in codes)
            if not old.next_cursor or old.next_cursor == str(cursor):
                break
            cursor = UUID(old.next_cursor)
        configured = self.auth.settings.ufsm_recommendation_extra_courses.split(",")
        observed = cached_offering_courses(self.auth, ano, semestre, codes)
        courses = [own, *sorted(({x.strip() for x in configured if x.strip()} | hints | observed) - {own})]
        offerings = {}
        for course in courses:
            path = "/ofertas?" + urlencode({"cursoCodigo": course, "ano": ano, "semestre": semestre})
            rows = await cached_academic_data(self.auth, self.token, path, ttl=OFFER_CACHE_TTL)
            for row in rows:
                if row.get("disciplinaCodigo") not in codes:
                    continue
                result = normalize_offering(row, set())
                if not result:
                    continue
                official_id = result["id"]
                offering_id = uuid5(NAMESPACE_URL, f"ufsm:oferta:{official_id}")
                offerings[offering_id] = OfertaTurma(
                    offering_id, course, self.snapshot["curriculo"].get("curso_nome") or course
                    if course == own else course,
                    result["disciplina_codigo"], result["disciplina_nome"], ano, semestre,
                    result["codigo_turma"], row.get("cargaHoraria") or 0, row.get("creditos") or 0,
                    row["situacao"], (), fonte_dados="UFSM",
                    horarios=tuple(HorarioOfertaTurma(
                        slot_idx, slot["dia_semana"], slot["dia_nome"],
                        time.fromisoformat(slot["hora_inicio"]), time.fromisoformat(slot["hora_fim"]), "",
                    ) for slot_idx, slot in enumerate(result["horarios"], start=1)),
                    id_institucional=official_id,
                )
        return Page(tuple(offerings.values()))
