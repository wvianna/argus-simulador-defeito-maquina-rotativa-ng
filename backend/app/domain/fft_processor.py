"""Processamento de FFT: extração de picos R^3, RMS e valor DC (FR-004, FR-005, FR-006, NFR-001)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .signal_generator import DEFECT_PROFILES

ORDEM_MAXIMA_PADRAO = 10.0
MARGEM_SIDEBAND = 2.0


class NyquistViolationError(ValueError):
    """Levantado quando a taxa de amostragem não respeita o critério de Nyquist (NFR-001)."""


@dataclass(frozen=True)
class Pico:
    frequencia_hz: float
    amplitude: float
    fase_graus: float


@dataclass(frozen=True)
class ResultadoFFT:
    picos: list[Pico]
    rms_total: float
    rms_ruido: float
    rms_picos: float
    valor_dc: float


def estimar_fmax_hz(rpm: float, tipo_defeito: str) -> float:
    """Estima a Fmax pretendida a partir da ordem harmônica mais alta do defeito.

    Os documentos de origem não definem um campo explícito de Fmax por simulação;
    esta é uma aproximação de engenharia (maior ordem do catálogo x margem de sideband),
    documentada como decisão em `.specs/features/simulador-vibracao/context.md`.
    """
    freq_rotacao_hz = rpm / 60.0
    perfil = DEFECT_PROFILES.get(tipo_defeito, [])
    ordem_maxima = max((c.ordem for c in perfil), default=ORDEM_MAXIMA_PADRAO)
    ordem_maxima = max(ordem_maxima, ORDEM_MAXIMA_PADRAO)
    return ordem_maxima * MARGEM_SIDEBAND * freq_rotacao_hz


def validar_nyquist(taxa_amostragem_hz: float, fmax_hz: float) -> None:
    if taxa_amostragem_hz <= 2 * fmax_hz:
        raise NyquistViolationError(
            f"Taxa de amostragem {taxa_amostragem_hz} Hz não respeita o critério de "
            f"Nyquist para Fmax={fmax_hz} Hz (mínimo exigido: {2 * fmax_hz} Hz)."
        )


def _encontrar_indices_picos(amplitudes: np.ndarray, limiar: float) -> list[int]:
    indices = []
    for i in range(1, len(amplitudes) - 1):
        if (
            amplitudes[i] > limiar
            and amplitudes[i] >= amplitudes[i - 1]
            and amplitudes[i] >= amplitudes[i + 1]
        ):
            indices.append(i)
    return indices


def calcular_picos(
    sinal: np.ndarray, taxa_amostragem_hz: float, limiar_relativo: float = 0.05, max_picos: int = 20
) -> list[Pico]:
    n = len(sinal)
    espectro = np.fft.rfft(sinal)
    freqs = np.fft.rfftfreq(n, d=1.0 / taxa_amostragem_hz)
    amplitudes = np.abs(espectro) * 2 / n
    fases = np.angle(espectro, deg=True)

    amplitude_max = float(amplitudes.max()) if amplitudes.size else 0.0
    limiar = amplitude_max * limiar_relativo
    indices = _encontrar_indices_picos(amplitudes, limiar)
    indices = sorted(indices, key=lambda i: amplitudes[i], reverse=True)[:max_picos]

    return [
        Pico(
            frequencia_hz=float(freqs[i]),
            amplitude=float(amplitudes[i]),
            fase_graus=float(fases[i]),
        )
        for i in indices
    ]


def calcular_rms_total(sinal: np.ndarray) -> float:
    return float(np.sqrt(np.mean(np.square(sinal))))


def calcular_rms_picos(picos: list[Pico]) -> float:
    energia = sum((p.amplitude / np.sqrt(2)) ** 2 for p in picos)
    return float(np.sqrt(energia))


def calcular_rms_ruido(rms_total: float, rms_picos: float) -> float:
    residual = rms_total**2 - rms_picos**2
    return float(np.sqrt(max(residual, 0.0)))


def calcular_valor_dc(sinal: np.ndarray) -> float:
    return float(np.mean(sinal))


def decimar_sinal(sinal: np.ndarray, max_pontos: int = 2000) -> list[float]:
    """Reduz o número de amostras retornadas ao front-end para exibição (FR-014).

    O sinal completo não é persistido (ver ADR em design.md); apenas uma versão
    decimada é devolvida na resposta da API para desenhar o gráfico do painel.
    """
    if len(sinal) <= max_pontos:
        return [float(v) for v in sinal]
    passo = len(sinal) // max_pontos
    return [float(v) for v in sinal[::passo][:max_pontos]]


def processar(sinal: np.ndarray, taxa_amostragem_hz: float, fmax_hz: float) -> ResultadoFFT:
    """Pipeline completo de FFT: valida Nyquist, extrai picos e calcula RMS/DC."""
    validar_nyquist(taxa_amostragem_hz, fmax_hz)
    picos = calcular_picos(sinal, taxa_amostragem_hz)
    rms_total = calcular_rms_total(sinal)
    rms_picos = calcular_rms_picos(picos)
    rms_ruido = calcular_rms_ruido(rms_total, rms_picos)
    valor_dc = calcular_valor_dc(sinal)
    return ResultadoFFT(
        picos=picos,
        rms_total=rms_total,
        rms_ruido=rms_ruido,
        rms_picos=rms_picos,
        valor_dc=valor_dc,
    )
