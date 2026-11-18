"""Fluxo de homologação DTI. Somente o backend conversa com a UFSM."""
import base64
import hashlib
import json
import re
import secrets
from asyncio import gather
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from math import ceil
from time import monotonic
from urllib.parse import SplitResult, parse_qsl, urlencode, urlsplit
from uuid import uuid4

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import ApplicationError, AuthenticationError, DataSourceUnavailableError, RateLimitError
from app.domain.entities import AuthSession, AuthUser, LoginResult, UserProfile
from app.services.ufsm_grade import build_grade

LOCAL_PREFIX = "ufsm_"
AUDIENCE = "provedor-trajetoria-academica"
_academic_tokens: dict[str, tuple[float, str]] = {}
_login_attempts: dict[str, float] = {}
LOGIN_ATTEMPT_TTL = 10 * 60
LOGIN_CONFIRMATION_TTL = 5 * 60


@dataclass(frozen=True, slots=True)
class PendingPortalLogin:
    person: int
    token: str
    token_expires: float
    confirmation_expires: float
    bindings: dict[int, dict]


_login_confirmations: dict[str, PendingPortalLogin] = {}


def _retry_after(value: str | None) -> int:
    if value:
        try:
            if value.isascii() and value.isdecimal() and len(value) <= 10:
                return max(1, int(value))
            return max(1, ceil((parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()))
        except (TypeError, ValueError, OverflowError):
            pass
    return 60


def _remember_academic_token(local_token: str, token: str, seconds: int) -> None:
    now = monotonic()
    for key, (expiry, _) in list(_academic_tokens.items()):
        if expiry <= now:
            del _academic_tokens[key]
    if len(_academic_tokens) >= 1024:
        del _academic_tokens[next(iter(_academic_tokens))]
    _academic_tokens[_digest(local_token)] = (now + seconds, token)


def require_enabled(settings: Settings) -> None:
    if not settings.ufsm_auth_enabled:
        raise ApplicationError("Login UFSM desabilitado.", status_code=404)


def _portal_login_url(settings: Settings) -> SplitResult:
    portal = urlsplit(settings.ufsm_portal_login_url)
    if portal.scheme != "https" or not portal.hostname or portal.username or portal.password or portal.fragment:
        raise DataSourceUnavailableError("Confira o endereço de login da UFSM no backend.")
    return portal


def portal_account_url(settings: Settings) -> str:
    # Sem clientId, o portal abre a própria conta, em vez de autorizar o app.
    return _portal_login_url(settings)._replace(query="").geturl()


def _digest(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


class UfsmAcademicResourceNotFoundError(DataSourceUnavailableError):
    """A API acadêmica respondeu 404 a uma consulta autenticada."""


class UfsmAuthService:
    def __init__(self, settings: Settings, session: AsyncSession):
        self.settings = settings
        self.session = session

    async def _request(self, base: str, path: str, *, body=None, token=None):
        parsed = urlsplit(base)
        if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
            raise DataSourceUnavailableError("Configure um endereço HTTPS institucional da UFSM.")
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        try:
            async with httpx.AsyncClient(timeout=12, follow_redirects=False, trust_env=False) as client:
                response = await client.request(
                    "POST" if body is not None else "GET",
                    f"{base.rstrip('/')}{path}", json=body, headers=headers,
                )
            if response.status_code == 429:
                raise RateLimitError(retry_after=_retry_after(response.headers.get("Retry-After")))
            if response.status_code == 401 and token:
                raise AuthenticationError("A sessão institucional expirou. Entre novamente pela UFSM.")
            if response.status_code == 404 and token and body is None:
                raise UfsmAcademicResourceNotFoundError("A UFSM não encontrou o recurso consultado.")
            if response.status_code in (400, 401, 403, 422) and path == "/auth/token":
                raise AuthenticationError("A UFSM não aceitou a troca do código. Inicie o login novamente. Se persistir, confira as configurações da integração.")
            if not response.is_success:
                raise DataSourceUnavailableError("A UFSM recusou a operação. Confira a configuração da integração.")
            return response.json()
        except (httpx.RequestError, ValueError):
            raise DataSourceUnavailableError("Não foi possível consultar a UFSM. Verifique a VPN.") from None

    async def _post(self, path, **body):
        return await self._request(self.settings.ufsm_auth_url, path, body={
            **body, "clientId": self.settings.ufsm_client_id,
        })

    def _require_secret(self):
        require_enabled(self.settings)
        if not self.settings.ufsm_client_secret or not self.settings.ufsm_client_secret.get_secret_value():
            raise DataSourceUnavailableError("UFSM_CLIENT_SECRET não configurado no backend.")
        return self.settings.ufsm_client_secret.get_secret_value()

    def start_portal_login(self, origin: str | None) -> tuple[str, str]:
        self._require_secret()
        portal = _portal_login_url(self.settings)
        callback = urlsplit(self.settings.ufsm_redirect_uri)
        callback_origin = f"{callback.scheme}://{callback.netloc}"
        if (
            not callback.hostname or callback.username or callback.password or callback.query or callback.fragment
            or callback.path != "/auth/callback"
            or not (callback.scheme == "https" or (callback.scheme == "http" and callback.hostname == "localhost"))
        ):
            raise DataSourceUnavailableError("Confira os endereços de login e de retorno da UFSM no backend.")
        if origin != callback_origin:
            raise ApplicationError(
                "Abra o app no endereço cadastrado para o retorno da UFSM.",
                code="ufsm_origem_invalida", status_code=403,
            )

        # O portal não devolve state no contrato atual. Além da tentativa
        # desta aba, exigimos confirmação explícita da conta após o retorno.
        now = monotonic()
        for key, expires in list(_login_attempts.items()):
            if expires <= now:
                del _login_attempts[key]
        if len(_login_attempts) >= 1024:
            del _login_attempts[next(iter(_login_attempts))]
        attempt = secrets.token_urlsafe(32)
        _login_attempts[_digest(attempt)] = now + LOGIN_ATTEMPT_TTL
        params = dict(parse_qsl(portal.query))
        params["clientId"] = self.settings.ufsm_client_id
        return portal._replace(query=urlencode(params)).geturl(), attempt

    async def complete_portal_login(self, code: str, attempt: str) -> dict:
        secret = self._require_secret()
        pending = _login_attempts.pop(_digest(attempt), None)
        if pending is None or pending <= monotonic():
            raise AuthenticationError("A tentativa de login expirou ou já foi usada. Volte e entre novamente pela UFSM.")
        exchanged = await self._post(
            "/auth/token", code=code, clientSecret=secret, redirectUri=self.settings.ufsm_redirect_uri,
        )
        token = exchanged.get("accessToken") if isinstance(exchanged, dict) else None
        if not isinstance(token, str):
            raise DataSourceUnavailableError("A UFSM não retornou o token de acesso.")

        # O token é obtido do servidor oficial via TLS, nunca do navegador.
        # O provedor acadêmico valida a assinatura antes de usar as claims.
        bindings = await self._request(
            self.settings.ufsm_academic_url, "/api/v1/me/vinculos-academicos", token=token,
        )
        try:
            claims = json.loads(base64.urlsafe_b64decode(token.split(".")[1] + "==="))
            if not isinstance(claims, dict):
                raise ValueError
            person = claims["idPessoa"]
            seconds = min(int(claims["exp"]) - int(datetime.now(timezone.utc).timestamp()), 3600)
            if (
                claims.get("iss") != "portal-autenticacao"
                or claims.get("azp") != self.settings.ufsm_client_id
                or claims.get("aud") not in ([AUDIENCE], AUDIENCE)
                or type(person) is not int or person <= 0 or seconds <= 0
            ):
                raise ValueError
        except (ValueError, IndexError, TypeError, KeyError, AttributeError):
            raise DataSourceUnavailableError("O token retornado não identifica uma sessão acadêmica válida.") from None
        current = {
            x["id"]: x for x in bindings
            if isinstance(x, dict) and x.get("regular") is True
            and all(isinstance(x.get(k), str) and x[k].strip() for k in ("matricula", "cursoCodigo", "nome"))
            and type(x.get("id")) is int and x["id"] > 0
        } if isinstance(bindings, list) else {}
        if not current:
            raise ApplicationError(
                "A conta autenticada não tem um vínculo acadêmico regular disponível na UFSM.",
                code="ufsm_vinculo_indefinido", status_code=403,
            )
        now = monotonic()
        for key, entry in list(_login_confirmations.items()):
            if entry.confirmation_expires <= now:
                del _login_confirmations[key]
        if len(_login_confirmations) >= 1024:
            del _login_confirmations[next(iter(_login_confirmations))]
        confirmation = secrets.token_urlsafe(32)
        _login_confirmations[_digest(confirmation)] = PendingPortalLogin(
            person, token, now + seconds, now + min(seconds, LOGIN_CONFIRMATION_TTL), current,
        )
        # Até a confirmação, não criamos sessão nem carregamos o histórico.
        return {
            "confirmacao": confirmation,
            "nome": next(iter(current.values()))["nome"],
            "vinculos": [
                {
                    "id": item["id"], "matricula": item["matricula"], "curso_codigo": item["cursoCodigo"],
                    "curso_nome": item["cursoNome"] if isinstance(item.get("cursoNome"), str) else None,
                }
                for item in current.values()
            ],
        }

    async def confirm_portal_login(self, confirmation: str, vinculo_id: int) -> LoginResult:
        require_enabled(self.settings)
        pending = _login_confirmations.pop(_digest(confirmation), None)
        if pending is None or pending.confirmation_expires <= monotonic():
            raise AuthenticationError("A confirmação de login expirou ou já foi usada. Entre novamente pela UFSM.")
        binding = pending.bindings.get(vinculo_id)
        if binding is None:
            raise ApplicationError(
                "O vínculo não pertence à conta autenticada na UFSM.",
                code="ufsm_vinculo_invalido", status_code=403,
            )
        grade = None
        if type(binding.get("ppcId")) is int and binding["ppcId"] > 0:
            try:
                grade = await self._load_grade(binding, pending.token)
            except (DataSourceUnavailableError, RateLimitError):
                # O plano e o questionário continuam acessíveis se a grade falhar.
                pass
        seconds = int(pending.token_expires - monotonic())
        if seconds <= 0:
            raise AuthenticationError("A sessão institucional expirou. Entre novamente pela UFSM.")
        result = await self._new_session(pending.person, binding, seconds, grade=grade)
        _remember_academic_token(result.sessao.access_token, pending.token, seconds)
        return result

    def academic_token(self, local_token: str) -> str:
        entry = _academic_tokens.get(_digest(local_token))
        if entry is None or entry[0] <= monotonic():
            _academic_tokens.pop(_digest(local_token), None)
            raise AuthenticationError("Entre novamente pela UFSM para consultar as ofertas.")
        return entry[1]

    async def _load_grade(self, binding: dict, token: str) -> dict:
        ppc = binding["ppcId"]
        vinculo = binding["id"]
        results = await gather(*(
            self._request(self.settings.ufsm_academic_url, f"/api/v1{path}", token=token)
            for path in (
                f"/ppcs/{ppc}", f"/ppcs/{ppc}/componentes",
                f"/me/historico?vinculo={vinculo}", f"/me/aproveitamentos?vinculo={vinculo}",
                f"/ppcs/{ppc}/equivalencias",
            )
        ))
        return build_grade(binding, *results)

    async def _new_session(self, person: int, binding: dict, seconds: int, *, grade=None) -> LoginResult:
        token = LOCAL_PREFIX + secrets.token_urlsafe(32)
        user_id = (await self.session.execute(text("""
            insert into public.usuario (id, ufsm_id_pessoa, nome)
            values (:id, :pessoa, :nome)
            on conflict (ufsm_id_pessoa) do update set nome = excluded.nome
            returning id
        """), {"id": uuid4(), "pessoa": person, "nome": binding["nome"]})).scalar_one()
        await self.session.execute(text("""
            insert into private.ufsm_sessao
            (token_hash, usuario_id, expira_em, matricula, curso_codigo, vinculo_id, grade_academica)
            values (:token, :user, :expires, :matricula, :curso, :vinculo, cast(:grade as jsonb))
        """), {
            "token": _digest(token), "user": user_id, "matricula": binding["matricula"],
            "curso": binding["cursoCodigo"], "vinculo": binding["id"],
            "grade": json.dumps(grade) if grade is not None else None,
            "expires": datetime.now(timezone.utc) + timedelta(seconds=seconds),
        })
        await self.session.execute(text("delete from private.ufsm_sessao where expira_em <= now()"))
        await self.session.commit()
        return LoginResult(
            usuario=AuthUser(user_id, ""),
            sessao=AuthSession(token, "", seconds, "bearer"),
            perfil=UserProfile(user_id, binding["matricula"], binding["cursoCodigo"], binding["nome"],
                               ppc_id=binding.get("ppcId")),
        )

    @staticmethod
    def _curriculum_id(grade):
        return grade.get("curriculo", {}).get("id") if isinstance(grade, dict) else None

    async def profile(self, token: str) -> UserProfile:
        if not self.settings.ufsm_auth_enabled or not re.fullmatch(r"ufsm_[A-Za-z0-9_-]{43}", token):
            raise AuthenticationError("Sessão UFSM inválida ou expirada.")
        row = (await self.session.execute(text("""
            select u.id, s.matricula, s.curso_codigo, u.nome, s.grade_academica
            from private.ufsm_sessao s join public.usuario u on u.id = s.usuario_id
            where s.token_hash = :token and s.expira_em > now()
              and u.ufsm_id_pessoa is not null
        """), {"token": _digest(token)})).one_or_none()
        if row is None:
            raise AuthenticationError("Sessão UFSM inválida ou expirada.")
        grade = row[4]
        completed = frozenset(
            component["disciplina_codigo"]
            for component in grade.get("componentes", [])
            if component.get("disciplina_codigo") and (component.get("tentativa_oficial") or {}).get("cumprido")
        ) if isinstance(grade, dict) else frozenset()
        return UserProfile(*row[:4], ppc_id=self._curriculum_id(grade), disciplinas_cumpridas_oficiais=completed)

    async def grade(self, token: str) -> dict:
        if not self.settings.ufsm_auth_enabled or not re.fullmatch(r"ufsm_[A-Za-z0-9_-]{43}", token):
            raise AuthenticationError("Sessão UFSM inválida ou expirada.")
        row = (await self.session.execute(text("""
            select grade_academica
            from private.ufsm_sessao
            where token_hash = :token and expira_em > now()
        """), {"token": _digest(token)})).one_or_none()
        if row is None:
            raise AuthenticationError("Sessão UFSM inválida ou expirada.")
        if row[0] is None:
            raise DataSourceUnavailableError(
                "Não foi possível carregar o PPC e o histórico oficiais. Confira a VPN e entre novamente."
            )
        return row[0]

    async def logout(self, token: str) -> None:
        await self.profile(token)
        await self.session.execute(text("delete from private.ufsm_sessao where token_hash = :token"), {
            "token": _digest(token),
        })
        await self.session.commit()
        _academic_tokens.pop(_digest(token), None)
