"""Repositório: leitura/gravação de leituras e cálculo de taxa de descarte (FR-009 a FR-013)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import LeituraPersistida, LeituraTrash, Ponto, SnapshotDefeito


async def obter_ponto(session: AsyncSession, ponto_id: uuid.UUID) -> Ponto | None:
    return await session.get(Ponto, ponto_id)


async def obter_ultima_leitura_persistida(
    session: AsyncSession, ponto_id: uuid.UUID
) -> LeituraPersistida | None:
    """Lê o Ponto com lock de linha (FOR UPDATE), evitando corrida entre simulações concorrentes."""
    resultado = await session.execute(select(Ponto).where(Ponto.id == ponto_id).with_for_update())
    ponto = resultado.scalar_one_or_none()
    if ponto is None or ponto.ultima_leitura_persistida_id is None:
        return None
    return await session.get(LeituraPersistida, ponto.ultima_leitura_persistida_id)


async def persistir_leitura(
    session: AsyncSession, ponto_id: uuid.UUID, dados: dict[str, Any]
) -> LeituraPersistida:
    leitura = LeituraPersistida(ponto_id=ponto_id, **dados)
    session.add(leitura)
    await session.flush()

    ponto = await session.get(Ponto, ponto_id)
    assert ponto is not None
    ponto.ultima_leitura_persistida_id = leitura.id

    await session.commit()
    return leitura


async def descartar_leitura(
    session: AsyncSession, ponto_id: uuid.UUID, dados: dict[str, Any], motivo: str
) -> LeituraTrash:
    leitura = LeituraTrash(ponto_id=ponto_id, motivo_descarte=motivo, **dados)
    session.add(leitura)
    await session.commit()
    return leitura


async def registrar_snapshot(
    session: AsyncSession,
    *,
    leitura_id: uuid.UUID,
    leitura_tipo: str,
    sensor_id: str,
    tipo_defeito: str,
) -> SnapshotDefeito:
    snapshot = SnapshotDefeito(
        leitura_id=leitura_id,
        leitura_tipo=leitura_tipo,
        sensor_id=sensor_id,
        tipo_defeito=tipo_defeito,
    )
    session.add(snapshot)
    await session.commit()
    return snapshot


async def leitura_existe(session: AsyncSession, leitura_id: uuid.UUID, leitura_tipo: str) -> bool:
    modelo = LeituraPersistida if leitura_tipo == "persistida" else LeituraTrash
    resultado = await session.get(modelo, leitura_id)
    return resultado is not None


async def calcular_taxa_descarte(session: AsyncSession, ponto_id: uuid.UUID) -> float:
    total_persistidas = await session.scalar(
        select(func.count())
        .select_from(LeituraPersistida)
        .where(LeituraPersistida.ponto_id == ponto_id)
    )
    total_trash = await session.scalar(
        select(func.count()).select_from(LeituraTrash).where(LeituraTrash.ponto_id == ponto_id)
    )
    total_persistidas = total_persistidas or 0
    total_trash = total_trash or 0
    total_avaliadas = total_persistidas + total_trash
    if total_avaliadas == 0:
        return 0.0
    return total_trash / total_avaliadas
