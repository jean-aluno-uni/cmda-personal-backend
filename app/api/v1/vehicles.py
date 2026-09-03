from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_owned_vehicle
from app.core.database import get_db
from app.models.veiculo import Veiculo
from app.schemas.veiculo import ConexaoResponse, VeiculoOut, VeiculoStatusOut
from app.services.veiculo_service import VeiculoService

router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/{veiculo_id}", response_model=VeiculoOut)
def get_vehicle(veiculo: Veiculo = Depends(get_owned_vehicle)):
    return VeiculoOut.model_validate(veiculo)


@router.get("/{veiculo_id}/status", response_model=VeiculoStatusOut)
def get_vehicle_status(veiculo: Veiculo = Depends(get_owned_vehicle)):
    return VeiculoStatusOut.model_validate(veiculo)


@router.post("/{veiculo_id}/connect", response_model=ConexaoResponse)
def connect_vehicle(veiculo: Veiculo = Depends(get_owned_vehicle), db: Session = Depends(get_db)):
    veiculo = VeiculoService(db).connect(veiculo)
    return ConexaoResponse(conectado=veiculo.conectado)


@router.post("/{veiculo_id}/disconnect", response_model=ConexaoResponse)
def disconnect_vehicle(veiculo: Veiculo = Depends(get_owned_vehicle), db: Session = Depends(get_db)):
    veiculo = VeiculoService(db).disconnect(veiculo)
    return ConexaoResponse(conectado=veiculo.conectado)
