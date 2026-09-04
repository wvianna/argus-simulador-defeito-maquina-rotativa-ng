"""Testes de contrato do endpoint POST /snapshots (CA-009)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.persistence.models import Ponto


def _payload_simulacao(ponto_id: str) -> dict:
    return {
        "ponto_id": ponto_id,
        "rpm": 1780,
        "tipo_defeito": "desbalanceamento",
        "severidade": 0.6,
        "ruido_fundo": 0.05,
        "taxa_amostragem_hz": 25600,
        "numero_amostras": 4096,
    }


@pytest.mark.asyncio
async def test_snapshot_registrado_com_sucesso(client: AsyncClient, ponto_seed: Ponto) -> None:
    simulacao = await client.post("/simulacoes", json=_payload_simulacao(str(ponto_seed.id)))
    leitura_id = simulacao.json()["leitura_id"]
    leitura_tipo = simulacao.json()["leitura_tipo"]

    resposta = await client.post(
        "/snapshots",
        json={
            "leitura_id": leitura_id,
            "leitura_tipo": leitura_tipo,
            "sensor_id": "SENSOR-01",
            "tipo_defeito": "desbalanceamento",
        },
    )

    assert resposta.status_code == 201
    corpo = resposta.json()
    assert "snapshot_id" in corpo
    assert "criado_em" in corpo


@pytest.mark.asyncio
async def test_snapshot_com_leitura_inexistente_retorna_404(client: AsyncClient) -> None:
    resposta = await client.post(
        "/snapshots",
        json={
            "leitura_id": "00000000-0000-0000-0000-000000000000",
            "leitura_tipo": "persistida",
            "sensor_id": "SENSOR-01",
            "tipo_defeito": "desbalanceamento",
        },
    )

    assert resposta.status_code == 404


@pytest.mark.asyncio
async def test_snapshot_com_tipo_defeito_invalido_retorna_422(
    client: AsyncClient, ponto_seed: Ponto
) -> None:
    simulacao = await client.post("/simulacoes", json=_payload_simulacao(str(ponto_seed.id)))
    leitura_id = simulacao.json()["leitura_id"]
    leitura_tipo = simulacao.json()["leitura_tipo"]

    resposta = await client.post(
        "/snapshots",
        json={
            "leitura_id": leitura_id,
            "leitura_tipo": leitura_tipo,
            "sensor_id": "SENSOR-01",
            "tipo_defeito": "inexistente",
        },
    )

    assert resposta.status_code == 422
