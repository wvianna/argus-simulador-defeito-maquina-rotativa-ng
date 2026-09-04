"""Schemas Pydantic dos contratos de API (ver .specs/features/simulador-vibracao/design.md)."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from ..domain.signal_generator import TIPOS_DEFEITO_VALIDOS


class SimulacaoRequest(BaseModel):
    ponto_id: uuid.UUID
    rpm: float = Field(gt=0)
    tipo_defeito: str
    severidade: float = Field(ge=0, le=1)
    ruido_fundo: float = Field(ge=0)
    taxa_amostragem_hz: float = Field(gt=0)
    numero_amostras: int = Field(gt=0, le=65536)
    # Limiar relativo (0..1) aplicado à FFT para descartar picos de ruído de fundo (FR-019).
    limiar_picos: float = Field(default=0.05, gt=0, le=1)

    @field_validator("tipo_defeito")
    @classmethod
    def validar_tipo_defeito(cls, v: str) -> str:
        if v not in TIPOS_DEFEITO_VALIDOS:
            raise ValueError(
                f"tipo_defeito inválido: {v!r}. Valores aceitos: {sorted(TIPOS_DEFEITO_VALIDOS)}"
            )
        return v


class PicoResponse(BaseModel):
    frequencia_hz: float
    amplitude: float
    fase_graus: float


class SimulacaoResponse(BaseModel):
    leitura_id: uuid.UUID
    leitura_tipo: str  # 'persistida' | 'trash'
    sinal_tempo: list[float]  # amostras decimadas do sinal (FR-014), não persistidas
    taxa_amostragem_hz: float
    limiar_picos: float  # limiar relativo usado na extração (FR-019)
    limiar_amplitude: float  # limiar absoluto (amplitude) para desenhar a linha no gráfico
    picos_r3: list[PicoResponse]
    rms_total: float
    rms_ruido: float
    rms_picos: float
    valor_dc: float
    rotacao: float
    descartada: bool
    motivo_descarte: str
    tempo_processamento_ms: float
    taxa_descarte_acumulada: float


class SnapshotRequest(BaseModel):
    leitura_id: uuid.UUID
    leitura_tipo: str = Field(pattern="^(persistida|trash)$")
    sensor_id: str
    tipo_defeito: str

    @field_validator("tipo_defeito")
    @classmethod
    def validar_tipo_defeito(cls, v: str) -> str:
        if v not in TIPOS_DEFEITO_VALIDOS:
            raise ValueError(f"tipo_defeito inválido: {v!r}")
        return v


class SnapshotResponse(BaseModel):
    snapshot_id: uuid.UUID
    criado_em: datetime
