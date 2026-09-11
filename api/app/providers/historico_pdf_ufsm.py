from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from io import BytesIO

import pdfplumber

from app.core.errors import ApplicationError
from app.domain.entities import HistoricoDocumento, ItemHistoricoDocumento


_STATUS = (
    "Aproveitamento por Adaptação",
    "Dispensa autodidatismo",
    "Dispensado com nota",
    "Dispensado sem nota",
    "Aprovado com nota",
    "Aprovado sem nota",
    "Reprovado por frequência",
    "Reprovado por nota",
    "Trancamento parcial",
    "Cancelamento de matrícula",
    "Não concluída",
    "Incompleto",
    "Matriculado",
)
_STATUS_PATTERN = re.compile(
    "(" + "|".join(re.escape(value) for value in _STATUS) + ")",
    re.IGNORECASE,
)
_SEMESTER_PATTERN = re.compile(r"^(\d)\.\s*Semestre de\s*(\d{4})$", re.IGNORECASE)
_GRADE_PATTERN = re.compile(r"^(\d{1,2},\d{2}|\*{3,})$")
_DISCIPLINE_START = re.compile(r"^([A-Z][A-Z0-9]{2,})\s+(.+)$")
_ADAPTATION_PREFIX_PATTERN = re.compile(r"Aproveitamento\s+por\s*$", re.IGNORECASE)
_CATEGORY_TITLES = {
    "DISCIPLINAS COMPLEMENTARES DE GRADUACAO",
    "DISCIPLINAS DE OUTROS CURSOS",
    "FORMACAO COMPLEMENTAR E HUMANISTICA",
    "NUCLEO DE FORMACAO BASICA",
    "NUCLEO DE FORMACO TECNOLOGICA",
    "NUCLEO DE FORMACAO TECNOLOGICA",
}


def _compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def _normalized(value: str) -> str:
    import unicodedata

    return "".join(
        char for char in unicodedata.normalize("NFD", value) if not unicodedata.combining(char)
    ).upper()


def _decimal(value: str | None) -> float | None:
    if not value or set(value) == {"*"}:
        return None
    return float(value.replace(".", "").replace(",", "."))


@dataclass
class _PendingItem:
    codigo: str
    nome: str
    carga_horaria: int
    creditos: int
    situacao: str
    ano: int
    semestre: int
    media: float | None
    dispensa: str | None
    categoria: str | None
    professores: list[str] = field(default_factory=list)
    teacher_mode: bool = False

    def finish(self) -> ItemHistoricoDocumento:
        return ItemHistoricoDocumento(
            codigo=self.codigo,
            nome=_compact(self.nome),
            carga_horaria=self.carga_horaria,
            creditos=self.creditos,
            situacao=_compact(self.situacao),
            ano=self.ano,
            semestre=self.semestre,
            media=self.media,
            dispensa=self.dispensa,
            categoria=self.categoria,
            professores=", ".join(dict.fromkeys(self.professores)) or None,
        )


class PdfUfsmHistoricoProvider:
    """Lê o histórico escolar textual emitido pelo portal da UFSM."""

    def read(self, content: bytes) -> HistoricoDocumento:
        if not content.startswith(b"%PDF"):
            self._invalid("O arquivo enviado não é um PDF válido.")

        try:
            with pdfplumber.open(BytesIO(content)) as pdf:
                pages = [
                    page.extract_text(layout=True, x_tolerance=2, y_tolerance=3) or ""
                    for page in pdf.pages
                ]
        except Exception as exc:
            raise ApplicationError(
                "Não foi possível abrir o PDF do histórico escolar.",
                code="historico_pdf_invalido",
                status_code=422,
            ) from exc

        text = "\n".join(pages)
        if "Histórico Escolar" not in text or "UNIVERSIDADE FEDERAL DE SANTA MARIA" not in text:
            self._invalid(
                "O documento não foi reconhecido como um histórico escolar textual da UFSM."
            )

        course = re.search(
            r"Curso:\s*([^\s]+)\s*-\s*(.*?)\s+Versão:\s*(\d{4})",
            text,
            re.IGNORECASE,
        )
        name = re.search(r"^\s*Nome:\s*(.+?)\s*$", text, re.MULTILINE)
        registration = re.search(r"^\s*Matrícula:\s*([^\s]+)", text, re.MULTILINE)
        if not course or not name or not registration:
            self._invalid("O cabeçalho do histórico está incompleto ou não pôde ser lido.")

        items = self._read_items(pages)
        if not items:
            self._invalid(
                "Nenhuma disciplina foi encontrada. PDFs digitalizados ainda não são suportados."
            )

        issued = re.search(r"Data:\s*(\d{2}/\d{2}/\d{4})", text)
        average = re.search(r"Média Geral Acumulada\s*\(MGA\)\s*:\s*(\d{1,2},\d{2})", text)
        total_hours = re.search(
            r"Total Carga Horária:\s*(\d+)\s+(\d+)\s+(\d+)", text
        )
        percentage = re.search(r"Percentual Vencido:\s*(\d+[\.,]\d+)\s*%", text)

        return HistoricoDocumento(
            curso_codigo=course.group(1).strip(),
            ppc_ano=int(course.group(3)),
            nome_aluno=_compact(name.group(1)),
            matricula=registration.group(1).strip(),
            data_emissao=(
                datetime.strptime(issued.group(1), "%d/%m/%Y").date() if issued else None
            ),
            itens=items,
            media_geral=_decimal(average.group(1)) if average else None,
            carga_horaria_realizada=int(total_hours.group(1)) if total_hours else None,
            carga_horaria_total=int(total_hours.group(2)) if total_hours else None,
            percentual_concluido=(
                float(percentage.group(1).replace(",", ".")) if percentage else None
            ),
        )

    def _read_items(self, pages: list[str]) -> tuple[ItemHistoricoDocumento, ...]:
        items: list[ItemHistoricoDocumento] = []
        pending: _PendingItem | None = None
        current_semester: tuple[int, int] | None = None
        current_category: str | None = None

        def finish_pending() -> None:
            nonlocal pending
            if pending is not None:
                items.append(pending.finish())
                pending = None

        for page in pages:
            for raw_line in page.splitlines():
                line = _compact(raw_line)
                if not line:
                    continue
                normalized = _normalized(line)

                if self._is_noise(normalized):
                    continue
                if normalized.startswith("CARGA HORARIA") or normalized.startswith("TOTAL CARGA HORARIA"):
                    finish_pending()
                    continue
                if normalized in _CATEGORY_TITLES:
                    finish_pending()
                    current_category = line
                    continue

                semester_match = _SEMESTER_PATTERN.match(line)
                if semester_match:
                    finish_pending()
                    current_semester = (int(semester_match.group(2)), int(semester_match.group(1)))
                    continue

                parsed = self._parse_discipline(line, current_semester, current_category)
                if parsed is not None:
                    finish_pending()
                    pending = parsed
                    if _normalized(pending.situacao) == "APROVEITAMENTO POR ADAPTACAO":
                        finish_pending()
                    continue

                if pending is None:
                    continue
                if _normalized(pending.situacao) == "APROVEITAMENTO POR":
                    adaptation_index = normalized.find("ADAPTACAO")
                    if adaptation_index >= 0:
                        name_continuation = _compact(line[:adaptation_index])
                        if name_continuation:
                            pending.nome = f"{pending.nome} {name_continuation}"
                        pending.situacao = "Aproveitamento por Adaptação"
                        tail = _compact(line[adaptation_index + len("ADAPTACAO") :])
                        if tail and _GRADE_PATTERN.fullmatch(tail):
                            pending.media = _decimal(tail)
                        finish_pending()
                        continue
                if line.lower().startswith("docente "):
                    pending.professores.append(_compact(line[8:]))
                    pending.teacher_mode = True
                    continue
                if _GRADE_PATTERN.fullmatch(line):
                    pending.media = _decimal(line)
                    continue
                if pending.teacher_mode:
                    if line == line.upper() and len(line) > 3:
                        pending.professores.append(line)
                    continue
                if line == line.upper() or re.fullmatch(r'"[A-Z]"', line):
                    pending.nome = f"{pending.nome} {line}"

        finish_pending()
        return tuple(items)

    @staticmethod
    def _parse_discipline(
        line: str,
        current_semester: tuple[int, int] | None,
        current_category: str | None,
    ) -> _PendingItem | None:
        if current_semester is None:
            return None
        start = _DISCIPLINE_START.match(line)
        if not start:
            return None
        status_match = _STATUS_PATTERN.search(start.group(2))
        adaptation_prefix = _ADAPTATION_PREFIX_PATTERN.search(start.group(2))
        if not status_match and not adaptation_prefix:
            return None

        match_start = status_match.start() if status_match else adaptation_prefix.start()
        before_status = _compact(start.group(2)[:match_start])
        prefix = re.match(r"^(.*?)\s+(\d{1,3})\s+(\d{1,2})$", before_status)
        if not prefix:
            return None

        match_end = status_match.end() if status_match else adaptation_prefix.end()
        tail = _compact(start.group(2)[match_end:])
        grade: float | None = None
        dispensa: str | None = None
        if tail:
            parts = tail.split()
            if parts and _GRADE_PATTERN.fullmatch(parts[-1]):
                grade = _decimal(parts.pop())
            if parts:
                dispensa = " ".join(parts)

        return _PendingItem(
            codigo=start.group(1),
            nome=prefix.group(1),
            carga_horaria=int(prefix.group(2)),
            creditos=int(prefix.group(3)),
            situacao=(status_match.group(1) if status_match else "Aproveitamento por"),
            ano=current_semester[0],
            semestre=current_semester[1],
            media=grade,
            dispensa=dispensa,
            categoria=current_category,
        )

    @staticmethod
    def _is_noise(normalized: str) -> bool:
        prefixes = (
            "UNIVERSIDADE FEDERAL DE SANTA MARIA",
            "HISTORICO ESCOLAR",
            "CURSO:",
            "NOME:",
            "MATRICULA:",
            "SITUACAO:",
            "FORMA DE INGRESSO:",
            "TIPO DOCUMENTO",
            "CADASTRO DE PESSOAS FISICAS",
            "CARTEIRA DE IDENTIDADE",
            "CODIGO DISCIPLINA",
            "AUTENTICACAO:",
            "OBSERVACOES:",
            "LOCAL ",
            "PERCENTUAL VENCIDO:",
            "MEDIA GERAL ACUMULADA",
            "FORMULA DE CALCULO",
            "MGA =",
            "MFD",
        )
        return normalized.startswith(prefixes) or normalized in {"DOCUMENTOS", "CARGA HORARIA"}

    @staticmethod
    def _invalid(message: str) -> None:
        raise ApplicationError(
            message,
            code="historico_pdf_invalido",
            status_code=422,
        )
