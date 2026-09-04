"""Ponto de entrada da aplicação FastAPI."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.simulacoes import router as simulacoes_router
from .api.snapshots import router as snapshots_router

app = FastAPI(title="Argus - Simulador de Defeito de Máquina Rotativa", version="0.1.0")

# Uso local sem autenticação (NFR-006): permite o front-end de desenvolvimento.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(simulacoes_router)
app.include_router(snapshots_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
