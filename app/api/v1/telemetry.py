from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_owned_vehicle
from app.core.database import get_db
from app.models.veiculo import Veiculo
from app.schemas.leitura import LeituraCreate, TelemetriaLatestOut, TemperatureHistoryPoint
from app.services.telemetria_service import TelemetriaService

router = APIRouter(prefix="/vehicles", tags=["telemetry"])


@router.get("/{veiculo_id}/telemetry/latest", response_model=TelemetriaLatestOut)
def get_latest_telemetry(veiculo: Veiculo = Depends(get_owned_vehicle), db: Session = Depends(get_db)):
    return TelemetriaService(db).obter_ultima(veiculo)


@router.post("/{veiculo_id}/readings", status_code=201)
def create_reading(
    dados: LeituraCreate,
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
):
    leitura = TelemetriaService(db).registrar_leitura(veiculo.id, dados)
    return {"id": leitura.id}


@router.get("/{veiculo_id}/temperature/history", response_model=list[TemperatureHistoryPoint])
def get_temperature_history(
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
    range: str = Query(default="7d", pattern="^(24h|7d|30d)$"),
):
    return TelemetriaService(db).obter_historico_temperatura(veiculo.id, range)
