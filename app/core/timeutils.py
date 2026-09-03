from datetime import datetime, timezone


def utcnow() -> datetime:
    """Datetime UTC 'naive' (sem tzinfo), usado para gravar e comparar contra colunas
    DATETIME do MySQL, que não guardam timezone. Mantém consistência entre o horário
    calculado pela aplicação e o que fica persistido no banco (evita descompasso entre
    `NOW()` do servidor MySQL, que reflete o relógio local do SO, e o UTC da aplicação)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def to_utc_naive(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt
    return dt.astimezone(timezone.utc).replace(tzinfo=None)
