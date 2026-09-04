"""Endpoint POST /snapshots — registra par sensor + anomalia para treinamento/RCA (FR-016)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..persistence import repository
from ..persistence.db import get_session
from . import schemas

router = APIRouter()


@router.post("/snapshots", response_model=schemas.SnapshotResponse, status_code=201)
async def criar_snapshot(
    payload: schemas.SnapshotRequest, session: AsyncSession = Depends(get_session)
) -> schemas.SnapshotResponse:
    existe = await repository.leitura_existe(session, payload.leitura_id, payload.leitura_tipo)
    if not existe:
        raise HTTPException(
            status_code=404, detail="leitura_id inexistente para o leitura_tipo informado"
        )

    snapshot = await repository.registrar_snapshot(
        session,
        leitura_id=payload.leitura_id,
        leitura_tipo=payload.leitura_tipo,
        sensor_id=payload.sensor_id,
        tipo_defeito=payload.tipo_defeito,
    )
    return schemas.SnapshotResponse(snapshot_id=snapshot.id, criado_em=snapshot.criado_em)
