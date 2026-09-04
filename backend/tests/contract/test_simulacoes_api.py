"""Testes de contrato do endpoint POST /simulacoes (CA-001, CA-002, CA-010, CA-011)."""

from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.persistence.models import Ponto


def _payload_valido(ponto_id: str) -> dict:
    return {
        "ponto_id": ponto_id,
        "rpm": 1780,
        "tipo_defeito": "desbalanceamento_estatico",
        "severidade": 0.6,
        "ruido_fundo": 0.05,
        "taxa_amostragem_hz": 25600,
        "numero_amostras": 4096,
    }


@pytest.mark.asyncio
async def test_simulacao_com_parametros_validos_retorna_200(
    client: AsyncClient, ponto_seed: Ponto
) -> None:
    resposta = await client.post("/simulacoes", json=_payload_valido(str(ponto_seed.id)))

    assert resposta.status_code == 200
    corpo = resposta.json()
    assert corpo["rotacao"] == 1780
    assert corpo["leitura_tipo"] in {"persistida", "trash"}
    assert "tempo_processamento_ms" in corpo


@pytest.mark.asyncio
async def test_simulacao_calcula_picos_e_rms(client: AsyncClient, ponto_seed: Ponto) -> None:
    resposta = await client.post("/simulacoes", json=_payload_valido(str(ponto_seed.id)))

    corpo = resposta.json()
    assert len(corpo["picos_r3"]) >= 1
    assert corpo["rms_total"] > 0
    assert "valor_dc" in corpo


@pytest.mark.asyncio
async def test_primeira_simulacao_do_ponto_e_sempre_persistida(
    client: AsyncClient, ponto_seed: Ponto
) -> None:
    resposta = await client.post("/simulacoes", json=_payload_valido(str(ponto_seed.id)))

    corpo = resposta.json()
    assert corpo["descartada"] is False
    assert corpo["leitura_tipo"] == "persistida"


@pytest.mark.asyncio
async def test_parametros_invalidos_retornam_422(client: AsyncClient, ponto_seed: Ponto) -> None:
    payload = _payload_valido(str(ponto_seed.id))
    payload["tipo_defeito"] = "inexistente"

    resposta = await client.post("/simulacoes", json=payload)

    assert resposta.status_code == 422


@pytest.mark.asyncio
async def test_violacao_de_nyquist_retorna_422(client: AsyncClient, ponto_seed: Ponto) -> None:
    payload = _payload_valido(str(ponto_seed.id))
    payload["taxa_amostragem_hz"] = 10  # muito baixa para o Fmax estimado de 1780 rpm

    resposta = await client.post("/simulacoes", json=payload)

    assert resposta.status_code == 422
    assert "Nyquist" in resposta.json()["detail"]


@pytest.mark.asyncio
async def test_ponto_inexistente_retorna_404(client: AsyncClient) -> None:
    payload = _payload_valido("00000000-0000-0000-0000-000000000000")

    resposta = await client.post("/simulacoes", json=payload)

    assert resposta.status_code == 404
