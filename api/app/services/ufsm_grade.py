"""Adapt the academic provider's official curriculum to the grade UI."""
from app.core.errors import DataSourceUnavailableError


def _items(value):
    if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
        raise DataSourceUnavailableError("A UFSM retornou dados acadêmicos inválidos.")
    return value


def _code(value):
    return str(value or "").upper().strip()


def _attempt(row):
    period = row.get("periodo") or {}
    status = row.get("situacao") or {}
    return {
        "disciplina_codigo": _code(row.get("disciplinaCodigo")),
        "disciplina": row.get("disciplinaNome"),
        "ano": period.get("ano"),
        "semestre": period.get("semestre"),
        "situacao_final": status.get("descricao"),
        "grupo_situacao": status.get("grupo"),
        "cumprido": status.get("cumprido") is True,
        "codigo_turma": (row.get("turma") or {}).get("codigo"),
        "media_final": row.get("mediaFinal"),
        "faltas_total": row.get("faltas"),
        "fonte": "UFSM",
    }


def build_grade(binding, ppc, raw_components, raw_history, raw_recognized, raw_equivalences):
    ppc_id = binding["ppcId"]
    if not isinstance(ppc, dict) or ppc.get("id") != ppc_id or ppc.get("cursoCodigo") != binding["cursoCodigo"]:
        raise DataSourceUnavailableError("A UFSM não retornou o PPC associado ao vínculo.")
    history = []
    dcg_attempts = {}
    fulfilled = {}
    by_component = {}
    for row in sorted(_items(raw_history), key=_chronology):
        attempt = _attempt(row)
        code = attempt["disciplina_codigo"]
        if not code:
            continue
        history.append(attempt)
        if attempt["cumprido"]:
            fulfilled[code] = attempt
        if _is_dcg(row) and (attempt["cumprido"] or not (dcg_attempts.get(code, {}).get("situacao") or {}).get("cumprido")):
            dcg_attempts[code] = row
    for row in _items(raw_recognized):
        attempt = _attempt(row)
        if row.get("ppcId") == ppc_id and attempt["cumprido"]:
            if row.get("ppcComponenteId") is not None:
                by_component[row["ppcComponenteId"]] = attempt
            if attempt["disciplina_codigo"]:
                fulfilled.setdefault(attempt["disciplina_codigo"], attempt)

    rules = _items(raw_equivalences)
    components = []
    complementary_hours = 0
    dcg_blocks = []
    for row in _items(raw_components):
        kind = row.get("tipoComponente")
        if kind in {"BLOCO_ACG", "BLOCO_ACEX"}:
            complementary_hours += row.get("cargaHoraria") or 0
            continue
        if kind == "BLOCO_DCG":
            dcg_blocks.append(row)
            continue
        if kind == "DCG":
            continue  # O catálogo não representa disciplinas que o estudante cursou.
        code = _code(row.get("disciplinaCodigo"))
        if not code:
            continue
        component = _component(row)
        recognized = by_component.get(row["id"]) or fulfilled.get(code)
        if not recognized:
            for rule in rules:
                groups = rule.get("grupos") or []
                if rule.get("ppcId") == ppc_id and rule.get("componenteId") == row["id"]:
                    matched = []
                    for group in groups:
                        codes = [_code(d.get("codigo")) for d in group.get("disciplinas") or []]
                        if codes and all(c in fulfilled for c in codes):
                            matched = [fulfilled[c] for c in codes]
                            break
                    if matched:
                        recognized = matched[-1]
                        break
                # A UFSM documenta equivalências simples nos dois sentidos;
                # não invertemos regras com alternativas ou grupos compostos.
                if rule.get("ppcId") != ppc_id and len(groups) == 1:
                    equivalents = groups[0].get("disciplinas") or []
                    other = _code(rule.get("disciplinaCodigo"))
                    if len(equivalents) == 1 and _code(equivalents[0].get("codigo")) == code and other in fulfilled:
                        recognized = fulfilled[other]
                        break
        if recognized:
            component["tentativa_oficial"] = {
                **recognized,
                "equivalencia_oficial": recognized["disciplina_codigo"] != code,
            }
        components.append(component)

    totals = {}
    represented = {item["disciplina_codigo"] for item in components}
    for code, row in dcg_attempts.items():
        if code in represented:
            continue
        structure = (row.get("estrutura") or {}).get("id")
        attempt = _attempt(row)
        if attempt["cumprido"]:
            totals[structure] = totals.get(structure, 0) + (row.get("cargaHoraria") or 0)
        components.append({
            **_component({**row, "id": f"ufsm-dcg-{code}", "nomeNoPpc": row.get("disciplinaNome"), "tipoComponente": "DCG"}),
            "tentativa_oficial": attempt,
        })
    for row in dcg_blocks:
        structure = (row.get("estrutura") or {}).get("id")
        remaining = max(0, (row.get("cargaHoraria") or 0) - totals.get(structure, 0))
        if remaining:
            components.append({**_component(row), "carga_horaria": remaining})

    return {
        "curriculo": {
            "id": ppc_id,
            "curso_nome": binding.get("cursoNome"),
            "ano_versao": ppc.get("anoVersao") or ppc.get("versao"),
            "nome": ppc.get("descricao") or ppc.get("versao"),
            "carga_horaria_total": ppc.get("cargaHorariaTotal"),
            "periodos_ideais": ppc.get("periodosIdeais"),
            "curriculo_corrente": ppc.get("curriculoCorrente"),
            "carga_horaria_extensao": ppc.get("cargaHorariaExtensao"),
            "horas_atividades_nao_acompanhadas": complementary_hours,
        },
        "componentes": components,
        "historico": history,
        "equivalencias": rules,
        "ano_ingresso": binding.get("anoIngresso"),
    }


def _chronology(row):
    period = row.get("periodo") or {}
    return (period.get("ano") or 0, period.get("codigo") or 0, row.get("id") or 0)


def _is_dcg(row):
    name = ((row.get("estrutura") or {}).get("nome") or "").casefold()
    return "disciplinas complementares" in name or "dcg" in name.split()


def _component(row):
    return {
        "id": row["id"],
        "disciplina_codigo": _code(row.get("disciplinaCodigo")) or None,
        "nome_no_ppc": row.get("nomeNoPpc"),
        "semestre_recomendado": row.get("semestreRecomendado") or None,
        "ordem_semestre": row.get("ordemSemestre"),
        "carga_horaria": row.get("cargaHoraria") or 0,
        "tipo_componente": row.get("tipoComponente"),
    }
