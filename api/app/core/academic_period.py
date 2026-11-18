from datetime import datetime
from zoneinfo import ZoneInfo


ACADEMIC_TIMEZONE = ZoneInfo("America/Sao_Paulo")


def current_academic_period(now: datetime | None = None) -> tuple[int, int]:
    local = datetime.now(ACADEMIC_TIMEZONE) if now is None else now.astimezone(ACADEMIC_TIMEZONE)
    return local.year, 1 if local.month <= 6 else 2
