from datetime import datetime, timezone


def utcnow() -> datetime:
    # sem tzinfo pra bater com as colunas DATETIME do mysql
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
