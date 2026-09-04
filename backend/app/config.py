"""Configuração via variáveis de ambiente (tolerâncias de descarte, conexão com banco)."""

from __future__ import annotations

import os

from .domain.discard_engine import Tolerancias

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+asyncpg://argus:argus@localhost:5432/argus"
)


def get_tolerancias() -> Tolerancias:
    """Tolerâncias do Paralelepípedo de Descarte e desvio de rotação, configuráveis via ambiente."""
    return Tolerancias(
        desvio_rotacao=float(os.environ.get("ARGUS_DESVIO_ROTACAO", "5.0")),
        delta_frequencia_hz=float(os.environ.get("ARGUS_DELTA_FREQUENCIA_HZ", "0.5")),
        delta_amplitude=float(os.environ.get("ARGUS_DELTA_AMPLITUDE", "0.1")),
        delta_fase_graus=float(os.environ.get("ARGUS_DELTA_FASE_GRAUS", "15.0")),
    )
