"""Endpoint POST /simulacoes — orquestra geração, FFT e motor de descarte (FR-014, FR-018)."""

from __future__ import annotations

import time
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import get_tolerancias
from ..domain import discard_engine, fft_processor, signal_generator
from ..observability.logging import log_simulacao
from ..persistence import repository
from ..persistence.db import get_session
from ..persistence.models import LeituraPersistida, LeituraTrash
from . import schemas

router = APIRouter()


@router.post("/simulacoes", response_model=schemas.SimulacaoResponse)
async def criar_simulacao(
    payload: schemas.SimulacaoRequest, session: AsyncSession = Depends(get_session)
) -> schemas.SimulacaoResponse:
    inicio = time.perf_counter()

    ponto = await repository.obter_ponto(session, payload.ponto_id)
    if ponto is None:
        raise HTTPException(status_code=404, detail="ponto_id inexistente")

    fmax_hz = fft_processor.estimar_fmax_hz(payload.rpm, payload.tipo_defeito)
    try:
        fft_processor.validar_nyquist(payload.taxa_amostragem_hz, fmax_hz)
    except fft_processor.NyquistViolationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    sinal = signal_generator.generate_signal(
        rpm=payload.rpm,
        tipo_defeito=payload.tipo_defeito,
        severidade=payload.severidade,
        ruido_fundo=payload.ruido_fundo,
        taxa_amostragem_hz=payload.taxa_amostragem_hz,
        numero_amostras=payload.numero_amostras,
        # Fase de referência estável por ponto (como um keyphasor), permitindo que
        # o Paralelepípedo de Descarte compare leituras sucessivas do mesmo ponto.
        semente_fase=payload.ponto_id.int,
    )
    resultado_fft = fft_processor.processar(
        sinal, payload.taxa_amostragem_hz, fmax_hz, limiar_relativo=payload.limiar_picos
    )

    ultima = await repository.obter_ultima_leitura_persistida(session, payload.ponto_id)
    leitura_atual = discard_engine.LeituraAvaliar(rotacao=payload.rpm, picos=resultado_fft.picos)
    ultima_avaliar = (
        discard_engine.LeituraAvaliar(
            rotacao=ultima.rotacao,
            picos=[fft_processor.Pico(**pico) for pico in ultima.picos_r3],
        )
        if ultima is not None
        else None
    )

    tolerancias = get_tolerancias()
    avaliacao = discard_engine.avaliar(leitura_atual, ultima_avaliar, tolerancias)

    dados = {
        "timestamp_original": datetime.now(UTC),
        "rotacao": payload.rpm,
        "picos_r3": [pico.__dict__ for pico in resultado_fft.picos],
        "rms_total": resultado_fft.rms_total,
        "rms_ruido": resultado_fft.rms_ruido,
        "rms_picos": resultado_fft.rms_picos,
        "valor_dc": resultado_fft.valor_dc,
    }

    if avaliacao.persistir:
        leitura: LeituraPersistida | LeituraTrash = await repository.persistir_leitura(
            session, payload.ponto_id, dados
        )
        leitura_tipo = "persistida"
    else:
        leitura = await repository.descartar_leitura(
            session, payload.ponto_id, dados, avaliacao.motivo
        )
        leitura_tipo = "trash"

    tempo_processamento_ms = (time.perf_counter() - inicio) * 1000
    taxa_descarte_acumulada = await repository.calcular_taxa_descarte(session, payload.ponto_id)

    log_simulacao(
        ponto_id=str(payload.ponto_id),
        decisao=avaliacao.decisao.value,
        tempo_processamento_ms=tempo_processamento_ms,
    )

    return schemas.SimulacaoResponse(
        leitura_id=leitura.id,
        leitura_tipo=leitura_tipo,
        sinal_tempo=fft_processor.decimar_sinal(sinal),
        taxa_amostragem_hz=payload.taxa_amostragem_hz,
        limiar_picos=payload.limiar_picos,
        limiar_amplitude=resultado_fft.limiar_absoluto,
        picos_r3=[schemas.PicoResponse(**pico.__dict__) for pico in resultado_fft.picos],
        rms_total=resultado_fft.rms_total,
        rms_ruido=resultado_fft.rms_ruido,
        rms_picos=resultado_fft.rms_picos,
        valor_dc=resultado_fft.valor_dc,
        rotacao=payload.rpm,
        descartada=not avaliacao.persistir,
        motivo_descarte=avaliacao.motivo,
        tempo_processamento_ms=tempo_processamento_ms,
        taxa_descarte_acumulada=taxa_descarte_acumulada,
    )
