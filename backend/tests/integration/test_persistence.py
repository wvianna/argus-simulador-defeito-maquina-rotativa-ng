"""Testes de persistência: ponteiro de última leitura e transações atômicas (FR-012, FR-013)."""

from __future__ import annotations

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence import repository
from app.persistence.models import Ponto


@pytest.mark.asyncio
async def test_persistir_leitura_atualiza_ponteiro_do_ponto(
    db_session: AsyncSession, ponto_seed: Ponto
) -> None:
    dados = {
        "rotacao": 1780.0,
        "picos_r3": [{"frequencia_hz": 29.7, "amplitude": 3.0, "fase_graus": 0.0}],
        "rms_total": 2.1,
        "rms_ruido": 0.1,
        "rms_picos": 2.0,
        "valor_dc": 0.0,
    }

    leitura = await repository.persistir_leitura(db_session, ponto_seed.id, dados)

    ponto_atualizado = await repository.obter_ponto(db_session, ponto_seed.id)
    assert ponto_atualizado is not None
    assert ponto_atualizado.ultima_leitura_persistida_id == leitura.id


@pytest.mark.asyncio
async def test_obter_ultima_leitura_persistida_retorna_none_sem_historico(
    db_session: AsyncSession, ponto_seed: Ponto
) -> None:
    ultima = await repository.obter_ultima_leitura_persistida(db_session, ponto_seed.id)
    assert ultima is None


@pytest.mark.asyncio
async def test_obter_ultima_leitura_persistida_retorna_a_mais_recente(
    db_session: AsyncSession, ponto_seed: Ponto
) -> None:
    dados_1 = {
        "rotacao": 1780.0,
        "picos_r3": [{"frequencia_hz": 29.7, "amplitude": 3.0, "fase_graus": 0.0}],
        "rms_total": 2.1,
        "rms_ruido": 0.1,
        "rms_picos": 2.0,
        "valor_dc": 0.0,
    }
    dados_2 = {**dados_1, "rotacao": 1800.0}

    primeira = await repository.persistir_leitura(db_session, ponto_seed.id, dados_1)
    segunda = await repository.persistir_leitura(db_session, ponto_seed.id, dados_2)

    ultima = await repository.obter_ultima_leitura_persistida(db_session, ponto_seed.id)
    assert ultima is not None
    assert ultima.id == segunda.id
    assert ultima.id != primeira.id


@pytest.mark.asyncio
async def test_descartar_leitura_nao_altera_ponteiro_do_ponto(
    db_session: AsyncSession, ponto_seed: Ponto
) -> None:
    dados = {
        "rotacao": 1780.0,
        "picos_r3": [{"frequencia_hz": 29.7, "amplitude": 3.0, "fase_graus": 0.0}],
        "rms_total": 2.1,
        "rms_ruido": 0.1,
        "rms_picos": 2.0,
        "valor_dc": 0.0,
    }
    leitura = await repository.persistir_leitura(db_session, ponto_seed.id, dados)

    await repository.descartar_leitura(db_session, ponto_seed.id, dados, "dentro da tolerância")

    ponto_atualizado = await repository.obter_ponto(db_session, ponto_seed.id)
    assert ponto_atualizado is not None
    assert ponto_atualizado.ultima_leitura_persistida_id == leitura.id  # inalterado


@pytest.mark.asyncio
async def test_calcular_taxa_descarte(db_session: AsyncSession, ponto_seed: Ponto) -> None:
    dados = {
        "rotacao": 1780.0,
        "picos_r3": [],
        "rms_total": 1.0,
        "rms_ruido": 0.1,
        "rms_picos": 0.9,
        "valor_dc": 0.0,
    }
    await repository.persistir_leitura(db_session, ponto_seed.id, dados)
    await repository.descartar_leitura(db_session, ponto_seed.id, dados, "motivo")
    await repository.descartar_leitura(db_session, ponto_seed.id, dados, "motivo")

    taxa = await repository.calcular_taxa_descarte(db_session, ponto_seed.id)
    assert taxa == pytest.approx(2 / 3)
