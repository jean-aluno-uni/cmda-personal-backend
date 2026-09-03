from fastapi import APIRouter

from app.api.v1 import alerts, auth, diagnostics, telemetry, users, vehicles

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(vehicles.router)
api_router.include_router(telemetry.router)
api_router.include_router(alerts.router)
api_router.include_router(diagnostics.router)
