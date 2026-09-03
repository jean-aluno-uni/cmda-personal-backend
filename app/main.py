import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.exceptions import AppError

# Requisito da Fase 01: o código OTP de recuperação de senha "não precisa enviar
# e-mail de verdade, basta logar" -- garantimos aqui que os loggers da aplicação
# (ex: app.services.auth_service) realmente aparecem no console do servidor.
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s [%(name)s] %(message)s")

app = FastAPI(
    title="CMDA Personal API",
    description="API do backend do CMDA Personal — Central de Mapeamento de Desempenho Automotivo.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(AppError)
def app_error_handler(_request: Request, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"error": exc.message})


app.include_router(api_router)


@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok"}
