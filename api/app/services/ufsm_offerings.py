from asyncio import Lock, sleep
from collections import OrderedDict
from datetime import time
from math import ceil
from time import monotonic
from unicodedata import normalize
from urllib.parse import parse_qs, urlencode

from app.core.academic_period import current_academic_period
from app.core.errors import ApplicationError, DataSourceUnavailableError, RateLimitError
from app.services.ufsm_auth import UfsmAcademicResourceNotFoundError

# Só dados de catálogo são compartilhados. A sessão é validada antes
# de consultar este cache; histórico e aprovações nunca entram nele.
_cache = OrderedDict()
_cache_locks = tuple(Lock() for _ in range(64))
ACTIVE = {"OFERTADA", "EM_ANDAMENTO"}
_upstream_lock = Lock()
_paused_until: dict[str, float] = {}
_throttled_catalogs: set[str] = set()
_last_request = 0.0
_min_request_interval = 0.8
_fallback_request_interval = 1.25
OFFER_CACHE_TTL = 1800


async def _fetch_catalog(auth, token, base, path):
    global _last_request
    async with _upstream_lock:
        remaining = ceil(_paused_until.get(base, 0) - monotonic())
        if remaining > 0:
            raise RateLimitError("A UFSM limitou temporariamente as consultas acadêmicas.", retry_after=remaining)
        interval = _fallback_request_interval if base in _throttled_catalogs else _min_request_interval
        delay = _last_request + interval - monotonic()
        if delay > 0:
            await sleep(delay)
        _last_request = monotonic()
        try:
            return await auth._request(base, f"/api/v1{path}", token=token)
        except RateLimitError as exc:
            seconds = exc.retry_after or 60
            _paused_until[base] = monotonic() + seconds
            _throttled_catalogs.add(base)
            raise RateLimitError("A UFSM limitou temporariamente as consultas acadêmicas.", retry_after=seconds) from None


async def cached_academic_data(auth, token, path, *, ttl=300, object_result=False, allow_missing=False):
    base = auth.settings.ufsm_academic_url
    key = (base, path)
    # Horários diferentes podem pedir as mesmas ofertas ao mesmo tempo.
    async with _cache_locks[hash(key) % len(_cache_locks)]:
        cached = _cache.get(key)
        if cached is not None and cached[0] > monotonic():
            _cache.move_to_end(key)
            if cached[1] is None and not allow_missing:
                raise UfsmAcademicResourceNotFoundError("A UFSM não encontrou o recurso consultado.")
            return cached[1]
        try:
            rows = await _fetch_catalog(auth, token, base, path)
        except UfsmAcademicResourceNotFoundError:
            if not allow_missing:
                raise
            rows = None
        else:
            valid = (isinstance(rows, dict) if object_result else
                     isinstance(rows, list) and all(isinstance(row, dict) for row in rows))
            if not valid:
                raise DataSourceUnavailableError("A UFSM retornou um catálogo inválido.")
        # Um código que hoje retorna 404 pode aparecer no catálogo depois.
        _cache[key] = (monotonic() + (ttl if rows is not None else min(ttl, 1800)), rows)
        _cache.move_to_end(key)
        if len(_cache) > 1024:
            _cache.popitem(last=False)
    return rows


async def _catalog(auth, token, path, ttl=300):
    return await cached_academic_data(auth, token, path, ttl=ttl)


def cached_offering_courses(auth, year, semester, codes):
    """Aproveita cursos consultados no Plano sem varrer a UFSM."""
    now = monotonic()
    courses = set()
    for (base, path), (expires, rows) in _cache.items():
        if base != auth.settings.ufsm_academic_url or expires <= now or not path.startswith("/ofertas?"):
            continue
        params = parse_qs(path.split("?", 1)[1])
        if (params.get("ano") == [str(year)] and params.get("semestre") == [str(semester)]
                and params.get("cursoCodigo") and any(row.get("disciplinaCodigo") in codes for row in rows)):
            courses.add(params["cursoCodigo"][0])
    return courses


def _sort_name(value):
    return normalize("NFKD", value).encode("ascii", "ignore").decode().casefold()


async def list_other_courses(auth, local_token):
    profile = await auth.profile(local_token)
    token = auth.academic_token(local_token)
    rows = await _catalog(auth, token, "/cursos", ttl=900)
    courses = sorted(
        ({"codigo": row["codigo"], "nome": row["nome"]} for row in rows
         if isinstance(row.get("codigo"), str) and isinstance(row.get("nome"), str)
         and row["codigo"] != profile.curso_codigo),
        key=lambda row: (_sort_name(row["nome"]), row["codigo"]),
    )
    return {"itens": courses}


def normalize_offering(row, approved, day=None, start=None, end=None):
    code = str(row.get("disciplinaCodigo") or "").strip().upper()
    if (not code or code in approved or row.get("situacao") not in ACTIVE
            or row.get("id") is None or not row.get("disciplinaNome")):
        return None
    meetings = []
    for slot in row.get("horarios") or []:
        try:
            weekday = slot["diaSemana"] - 1  # DTI: domingo=1; Plano: segunda=1.
            first, last = time.fromisoformat(slot["horaInicio"]), time.fromisoformat(slot["horaFim"])
            if weekday not in range(1, 6) or first >= last or first.tzinfo or last.tzinfo:
                return None  # Não adicione apenas parte de uma turma.
        except (KeyError, ValueError, TypeError):
            return None
        meetings.append((weekday, first, last, slot.get("diaSemanaDescricao") or ["", "Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira"][weekday]))
    if not meetings or (day is not None and not any(
        weekday == day and first < end and start < last for weekday, first, last, _ in meetings
    )):
        return None
    # O plano é semanal. Une trechos teóricos/práticos contíguos ou
    # duplicados para não criar conflitos da turma com ela mesma.
    merged = []
    for weekday, first, last, name in sorted(meetings):
        if merged and merged[-1][0] == weekday and first <= merged[-1][2]:
            previous = merged[-1]
            merged[-1] = (weekday, previous[1], max(previous[2], last), previous[3])
        else:
            merged.append((weekday, first, last, name))
    return {
        "id": f"ufsm-{row['id']}", "curso_codigo": row.get("cursoCodigo"),
        "disciplina_codigo": code, "disciplina_nome": row["disciplinaNome"],
        "codigo_turma": row.get("codigoTurma") or str(row["id"]),
        "horarios": [
            {"dia_semana": weekday, "dia_nome": name,
             "hora_inicio": first.isoformat(), "hora_fim": last.isoformat()}
            for weekday, first, last, name in merged
        ],
    }


async def _plan_context(auth, local_token, start, end):
    if start.tzinfo or end.tzinfo or end <= start:
        raise ApplicationError("O fim do intervalo deve ser posterior ao início.")
    profile = await auth.profile(local_token)
    token = auth.academic_token(local_token)
    grade = await auth.grade(local_token)
    approved = {
        item["disciplina_codigo"] for item in grade["historico"] if item.get("cumprido")
    } | {
        item["disciplina_codigo"] for item in grade["componentes"]
        if item.get("disciplina_codigo") and (item.get("tentativa_oficial") or {}).get("cumprido")
    }
    year, semester = current_academic_period()
    return profile, token, approved, year, semester


async def _course_offerings(auth, token, course, year, semester, approved, day, start, end):
    rows = await _catalog(auth, token, "/ofertas?" + urlencode({
        "cursoCodigo": course, "ano": year, "semestre": semester,
    }), ttl=OFFER_CACHE_TTL)
    offerings = {}
    for row in rows:
        normalized = normalize_offering(row, approved, day, start, end)
        if normalized is not None:
            offerings[normalized["id"]] = normalized
    return sorted(
        offerings.values(), key=lambda x: (_sort_name(x["disciplina_nome"]), x["codigo_turma"], x["id"]),
    )


async def list_offerings(auth, local_token, course, day, start, end):
    profile, token, approved, year, semester = await _plan_context(auth, local_token, start, end)
    items = await _course_offerings(auth, token, course or profile.curso_codigo, year, semester, approved, day, start, end)
    return {"ano": year, "semestre": semester, "itens": items}
