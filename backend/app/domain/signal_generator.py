"""Geração de sinal de vibração sintético a partir do catálogo de defeitos (FR-001 a FR-003)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ComponenteHarmonico:
    ordem: float  # múltiplo da frequência de rotação (1X)
    amplitude_relativa: float  # 0..1, escalada pela severidade
    sidebands: bool = False


# Catálogo de defeitos suportados (ver SPECIFICATION.md). Ordens são aproximações
# de engenharia documentadas em docs/criterioDetermincacaoAnamalia.txt; não há
# valores numéricos exatos na fonte, apenas relações qualitativas (ex.: "1X dominante",
# "harmônicos 1X-10X"). Ajustáveis conforme calibração futura.
DEFECT_PROFILES: dict[str, list[ComponenteHarmonico]] = {
    "desbalanceamento_estatico": [ComponenteHarmonico(1.0, 1.0)],
    "desbalanceamento_acoplamento": [ComponenteHarmonico(1.0, 1.0)],
    "desbalanceamento_dinamico": [ComponenteHarmonico(1.0, 1.0), ComponenteHarmonico(2.0, 0.15)],
    "desalinhamento_angular": [ComponenteHarmonico(1.0, 0.6), ComponenteHarmonico(2.0, 0.8)],
    "desalinhamento_paralelo": [
        ComponenteHarmonico(2.0, 1.0),
        ComponenteHarmonico(3.0, 0.3),
        ComponenteHarmonico(4.0, 0.15),
    ],
    "folga_tipo_a": [ComponenteHarmonico(1.0, 1.0)],
    "folga_tipo_b_c": [ComponenteHarmonico(float(n), 1.0 / n) for n in range(1, 11)],
    "oil_whirl": [ComponenteHarmonico(0.45, 1.0)],
    "oil_whip": [ComponenteHarmonico(0.45, 1.2)],
    "rotor_rub": [ComponenteHarmonico(0.5, 0.8), ComponenteHarmonico(1.0, 0.4)],
    "desgaste_rolamento_bpfo": [ComponenteHarmonico(3.5, 1.0, sidebands=True)],
    "desgaste_rolamento_bpfi": [ComponenteHarmonico(5.4, 1.0, sidebands=True)],
    "desgaste_rolamento_bsf": [ComponenteHarmonico(2.3, 1.0, sidebands=True)],
    "desgaste_rolamento_ftf": [ComponenteHarmonico(0.4, 1.0, sidebands=True)],
    "cavitacao": [],
    "erro_sensor": [ComponenteHarmonico(0.05, 1.0)],
}

TIPOS_DEFEITO_VALIDOS = frozenset(DEFECT_PROFILES.keys())


def generate_signal(
    *,
    rpm: float,
    tipo_defeito: str,
    severidade: float,
    ruido_fundo: float,
    taxa_amostragem_hz: float,
    numero_amostras: int,
    rng: np.random.Generator | None = None,
    semente_fase: int | None = None,
) -> np.ndarray:
    """Gera o sinal de vibração sintético no domínio do tempo (FR-003).

    `semente_fase` torna a fase das harmônicas determinística (referência de
    keyphasor estável por ponto de medição). Sem ela, a fase é sorteada a cada
    chamada. O ruído permanece variável (usado de `rng` ou um gerador novo).
    """
    if tipo_defeito not in DEFECT_PROFILES:
        raise ValueError(f"tipo_defeito desconhecido: {tipo_defeito!r}")

    rng_ruido = rng if rng is not None else np.random.default_rng()
    if semente_fase is not None:
        rng_fase = np.random.default_rng(semente_fase)
    else:
        rng_fase = rng_ruido
    freq_rotacao_hz = rpm / 60.0
    t = np.arange(numero_amostras) / taxa_amostragem_hz
    sinal = np.zeros(numero_amostras)

    for componente in DEFECT_PROFILES[tipo_defeito]:
        freq = componente.ordem * freq_rotacao_hz
        amplitude = componente.amplitude_relativa * severidade
        fase = rng_fase.uniform(0, 2 * np.pi)
        sinal += amplitude * np.sin(2 * np.pi * freq * t + fase)
        if componente.sidebands:
            for freq_lateral in (freq - freq_rotacao_hz, freq + freq_rotacao_hz):
                if freq_lateral > 0:
                    sinal += (amplitude * 0.3) * np.sin(
                        2 * np.pi * freq_lateral * t + rng_fase.uniform(0, 2 * np.pi)
                    )

    ruido_efetivo = max(ruido_fundo, 0.3) if tipo_defeito == "cavitacao" else ruido_fundo
    sinal += rng_ruido.normal(0, ruido_efetivo, numero_amostras)

    if tipo_defeito == "erro_sensor":
        sinal += np.linspace(0, severidade, numero_amostras)  # deriva térmica ("ski-slope")

    return sinal
