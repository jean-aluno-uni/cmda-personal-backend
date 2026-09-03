from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_owned_vehicle
from app.core.database import get_db
from app.models.veiculo import Veiculo
from app.schemas.diagnostico import DiagnosticoCreate, DiagnosticoOut
from app.services.diagnostico_service import DiagnosticoService

router = APIRouter(prefix="/vehicles", tags=["diagnostics"])


@router.get("/{veiculo_id}/diagnostics", response_model=DiagnosticoOut)
def get_diagnostics(
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
    indicadores: str | None = Query(default=None, description="Lista separada por vírgula, ex: RPM,Velocidade"),
):
    lista = [item.strip() for item in indicadores.split(",")] if indicadores else None
    diagnostico = DiagnosticoService(db).obter_diagnostico(veiculo.id, lista)
    if diagnostico is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Nenhum diagnóstico registrado para este veículo")
    return diagnostico


@router.post("/{veiculo_id}/diagnostics", response_model=DiagnosticoOut, status_code=201)
def create_diagnostics(
    dados: DiagnosticoCreate,
    veiculo: Veiculo = Depends(get_owned_vehicle),
    db: Session = Depends(get_db),
):
    return DiagnosticoService(db).registrar_diagnostico(veiculo.id, dados)
