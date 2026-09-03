from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.core.timeutils import utcnow
from app.repositories.alerta_repository import AlertaRepository
from app.schemas.alerta import AlertaCreate, AlertaListOut, AlertaOut, AlertaSummaryOut, OrigemAlertaResumo

_RANGE_PARA_TIMEDELTA = {
    "24h": timedelta(hours=24),
    "7d": timedelta(days=7),
    "30d": timedelta(days=30),
}

# Mesma paleta já usada no frontend mock (js/dados.js -> origemAlertas), reaproveitada
# aqui para manter o contrato visual do donut chart de origem dos alertas.
_COR_POR_ORIGEM = {
    "Motor": "#C2182B",
    "Transmissao": "#3B82F6",
    "Transmissão": "#3B82F6",
    "Bateria": "#10B981",
}
_COR_PADRAO = "#9CA3AF"


class AlertaService:
    """RN-004/RN-011: alertas sempre vinculados a um veículo específico (posse já
    validada na dependency de rota). RN-007: cada alerta carrega origem, descrição,
    nível e situação suficientes para o usuário entender a ocorrência."""

    def __init__(self, db: Session):
        self.repo = AlertaRepository(db)

    def registrar_alerta(self, veiculo_id: int, dados: AlertaCreate):
        payload = dados.model_dump(exclude_none=True)
        return self.repo.create(veiculo_id, payload)

    @staticmethod
    def _desde(period: str) -> datetime:
        delta = _RANGE_PARA_TIMEDELTA.get(period, _RANGE_PARA_TIMEDELTA["24h"])
        return utcnow() - delta

    def resumo(self, veiculo_id: int, period: str) -> AlertaSummaryOut:
        desde = self._desde(period)
        origens = self.repo.resumo_por_origem(veiculo_id, desde)
        total = sum(qtd for _, qtd in origens)

        origem_alertas = [
            OrigemAlertaResumo(
                local=origem,
                percentual=round((qtd / total) * 100, 2) if total else 0,
                cor=_COR_POR_ORIGEM.get(origem, _COR_PADRAO),
            )
            for origem, qtd in origens
        ]

        itens, _ = self.repo.list_by_periodo(veiculo_id, desde, page=1, page_size=5)
        tabela = [AlertaOut.model_validate(item) for item in itens]

        return AlertaSummaryOut(total=total, origem_alertas=origem_alertas, tabela_alertas=tabela)

    def listar(self, veiculo_id: int, period: str, page: int, page_size: int) -> AlertaListOut:
        desde = self._desde(period)
        itens, total = self.repo.list_by_periodo(veiculo_id, desde, page, page_size)
        return AlertaListOut(
            items=[AlertaOut.model_validate(item) for item in itens],
            total=total,
            page=page,
            page_size=page_size,
        )
