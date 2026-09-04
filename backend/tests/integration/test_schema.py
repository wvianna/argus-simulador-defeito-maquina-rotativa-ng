"""Testes de schema: cria as tabelas e valida inserção mínima por tabela (T-001)."""

from __future__ import annotations

import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.persistence.models import (
    Area,
    LeituraPersistida,
    LeituraTrash,
    Maquina,
    Planta,
    Ponto,
    SnapshotDefeito,
)


@pytest.mark.asyncio
async def test_schema_permite_inserir_hierarquia_completa(db_session: AsyncSession) -> None:
    planta = Planta(id=uuid.uuid4(), nome="Planta 1")
    area = Area(id=uuid.uuid4(), planta_id=planta.id, nome="Área 1")
    maquina = Maquina(id=uuid.uuid4(), area_id=area.id, nome="Máquina 1")
    ponto = Ponto(id=uuid.uuid4(), maquina_id=maquina.id, nome="Ponto 1")

    db_session.add_all([planta, area, maquina, ponto])
    await db_session.commit()

    resultado = await db_session.execute(select(Ponto).where(Ponto.id == ponto.id))
    assert resultado.scalar_one().nome == "Ponto 1"


@pytest.mark.asyncio
async def test_schema_permite_inserir_leitura_persistida_e_trash(
    db_session: AsyncSession, ponto_seed: Ponto
) -> None:
    leitura = LeituraPersistida(
        id=uuid.uuid4(),
        ponto_id=ponto_seed.id,
        rotacao=1780.0,
        picos_r3=[{"frequencia_hz": 29.7, "amplitude": 3.0, "fase_graus": 0.0}],
        rms_total=2.1,
        rms_ruido=0.1,
        rms_picos=2.0,
        valor_dc=0.0,
    )
    trash = LeituraTrash(
        id=uuid.uuid4(),
        ponto_id=ponto_seed.id,
        rotacao=1780.0,
        picos_r3=[{"frequencia_hz": 29.7, "amplitude": 3.0, "fase_graus": 0.0}],
        rms_total=2.1,
        rms_ruido=0.1,
        rms_picos=2.0,
        valor_dc=0.0,
        motivo_descarte="Todos os picos dentro da tolerância R^3",
    )
    db_session.add_all([leitura, trash])
    await db_session.commit()

    assert (await db_session.get(LeituraPersistida, leitura.id)) is not None
    assert (await db_session.get(LeituraTrash, trash.id)) is not None


@pytest.mark.asyncio
async def test_schema_permite_inserir_snapshot_defeito(
    db_session: AsyncSession, ponto_seed: Ponto
) -> None:
    leitura = LeituraPersistida(
        id=uuid.uuid4(),
        ponto_id=ponto_seed.id,
        rotacao=1780.0,
        picos_r3=[],
        rms_total=1.0,
        rms_ruido=0.1,
        rms_picos=0.9,
        valor_dc=0.0,
    )
    db_session.add(leitura)
    await db_session.commit()

    snapshot = SnapshotDefeito(
        id=uuid.uuid4(),
        leitura_id=leitura.id,
        leitura_tipo="persistida",
        sensor_id="SENSOR-01",
        tipo_defeito="desbalanceamento_estatico",
    )
    db_session.add(snapshot)
    await db_session.commit()

    assert (await db_session.get(SnapshotDefeito, snapshot.id)) is not None
