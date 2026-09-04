"""Logs estruturados e métrica de taxa de descarte (NFR-002, NFR-004)."""

from __future__ import annotations

import json
import logging
import time

logger = logging.getLogger("argus")


def log_simulacao(*, ponto_id: str, decisao: str, tempo_processamento_ms: float) -> None:
    """Registra um log estruturado (JSON) para cada simulação processada."""
    logger.info(
        json.dumps(
            {
                "evento": "simulacao_processada",
                "ponto_id": ponto_id,
                "decisao": decisao,
                "tempo_processamento_ms": round(tempo_processamento_ms, 3),
                "timestamp": time.time(),
            }
        )
    )


def calcular_taxa_descarte(total_descartadas: int, total_avaliadas: int) -> float:
    """Taxa de descarte agregada = leituras descartadas / leituras avaliadas (NFR-004)."""
    if total_avaliadas == 0:
        return 0.0
    return total_descartadas / total_avaliadas
