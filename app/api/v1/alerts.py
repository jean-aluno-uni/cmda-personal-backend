from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_owned_vehicle
from app.core.database import get_db
from app.models.veiculo import Veiculo
from app.schemas.alerta import AlertaCreate, AlertaListOut, AlertaSummaryOut
from app.services.alerta_service import AlertaService

router = APIRouter(prefix="/vehicles", tags=["alerts"])

_PeriodQuery = Query(default="24h", pattern="^(24h|7d|30d)$")


@router.get("/{veiculo_id}/alerts/summary", response_model=AlertaSummaryOut)
def get_alerts_summary(
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
    period: str = _PeriodQuery,
):
    return AlertaService(db).resumo(veiculo.id, period)


@router.get("/{veiculo_id}/alerts", response_model=AlertaListOut)
def list_alerts(
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
    period: str = _PeriodQuery,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100, alias="pageSize"),
):
    return AlertaService(db).listar(veiculo.id, period, page, page_size)


@router.post("/{veiculo_id}/alerts", status_code=201)
def create_alert(
    dados: AlertaCreate,
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
):
    alerta = AlertaService(db).registrar_alerta(veiculo.id, dados)
    return {"id": alerta.id}
