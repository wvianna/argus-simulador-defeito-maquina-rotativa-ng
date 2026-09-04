"""Geração de sinal de vibração sintético a partir das assinaturas espectrais (FR-001 a FR-003).

O catálogo e as ordens/pesos seguem `docs/assinaturas_fft_falhas_maquinas_rotativas_IA.md`.
As frequências são sempre calculadas a partir de `fr = RPM / 60`; amplitudes são pesos
relativos normalizados (o maior vale 1,0) escalados pela severidade, com ruído aditivo.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Componente:
    ordem: float  # múltiplo de fr (1X)
    peso: float  # peso relativo 0..1 (1,0 = componente dominante)
    sidebands_1x: bool = False  # gerar bandas laterais em ±1X


# Parâmetros construtivos padrão de rolamento (exemplo). A geometria real deve
# ser fornecida para calcular BPFO/BPFI/BSF/FTF — ver o documento de assinaturas.
_BEARING = {"n": 9, "bd_pd": 0.2, "phi_rad": 0.0}


def _ordem_rolamento(tipo: str) -> float:
    n = _BEARING["n"]
    r = _BEARING["bd_pd"]
    c = np.cos(_BEARING["phi_rad"])
    if tipo == "bpfo":
        return (n / 2.0) * (1.0 - r * c)
    if tipo == "bpfi":
        return (n / 2.0) * (1.0 + r * c)
    if tipo == "bsf":
        return (1.0 / (2.0 * r)) * (1.0 - (r * c) ** 2)
    if tipo == "ftf":
        return 0.5 * (1.0 - r * c)
    raise ValueError(f"tipo de rolamento desconhecido: {tipo!r}")


def _componentes_rolamento(tipo: str) -> list[Componente]:
    base = _ordem_rolamento(tipo)
    return [
        Componente(base, 1.00, sidebands_1x=(tipo in {"bpfo", "bpfi"})),
        Componente(2 * base, 0.40, sidebands_1x=(tipo in {"bpfo", "bpfi"})),
        Componente(3 * base, 0.20, sidebands_1x=(tipo in {"bpfo", "bpfi"})),
    ]


DEFECT_PROFILES: dict[str, list[Componente]] = {
    # 4. Sem defeito — 1X residual baixo, sem sequência forte de harmônicos.
    "sem_defeito": [Componente(1.0, 0.20), Componente(2.0, 0.03), Componente(3.0, 0.015)],
    # 5. Desbalanceamento — 1X dominante.
    "desbalanceamento": [Componente(1.0, 1.00), Componente(2.0, 0.07), Componente(3.0, 0.04)],
    # 7. Desalinhamento angular — 2X elevado + 1X + fracionários 1,5X/2,5X.
    "desalinhamento_angular": [
        Componente(1.0, 0.50),
        Componente(2.0, 0.80),
        Componente(3.0, 0.25),
        Componente(1.5, 0.15),
        Componente(2.5, 0.12),
        Componente(4.0, 0.12),
    ],
    # 8. Desalinhamento paralelo — 2X dominante + harmônicos pares.
    "desalinhamento_paralelo": [
        Componente(1.0, 0.40),
        Componente(2.0, 1.00),
        Componente(4.0, 0.40),
        Componente(6.0, 0.18),
        Componente(8.0, 0.08),
    ],
    # 9. Roçamento rotor-estator — 1X + série de harmônicos; sub-harmônicos quando severo.
    "rocamento": [
        Componente(1.0, 1.00),
        Componente(2.0, 0.50),
        Componente(3.0, 0.30),
        Componente(4.0, 0.20),
        Componente(5.0, 0.12),
    ],
    # 15. Mancal/suporte frouxo — família de harmônicos 1X..10X + fracionários.
    "mancal_frouxo": [
        Componente(1.0, 0.70),
        Componente(2.0, 0.60),
        Componente(3.0, 0.50),
        Componente(4.0, 0.40),
        Componente(5.0, 0.30),
        Componente(6.0, 0.24),
        Componente(7.0, 0.18),
        Componente(8.0, 0.14),
        Componente(9.0, 0.10),
        Componente(10.0, 0.08),
    ],
    # 16. Acoplamento defeituoso — 1X/2X + 3X/4X.
    "acoplamento_defeituoso": [
        Componente(1.0, 0.55),
        Componente(2.0, 0.75),
        Componente(3.0, 0.30),
        Componente(4.0, 0.15),
    ],
    # 18. Oil whirl — razão 0,39X..0,48X amostrada em tempo de geração.
    "oil_whirl": [],
    # 19. Whirl por atrito — sem razão universal; faixa paramétrica (hipotética).
    "whirl_atrito": [],
    # 10–13. Rolamentos (BPFO/BPFI/BSF/FTF) — calculados a partir da geometria.
    "rolamento_bpfo": _componentes_rolamento("bpfo"),
    "rolamento_bpfi": _componentes_rolamento("bpfi"),
    "rolamento_bsf": _componentes_rolamento("bsf"),
    "rolamento_ftf": _componentes_rolamento("ftf"),
}

TIPOS_DEFEITO_VALIDOS = frozenset(DEFECT_PROFILES.keys())

# Sub-harmônicos adicionais (amplitude crescente com a severidade para defeitos não lineares).
_SUB_HARMONICOS: dict[str, list[tuple[float, float]]] = {
    "rocamento": [(0.5, 0.50), (1 / 3, 0.35), (2 / 3, 0.30)],
    "mancal_frouxo": [(0.5, 0.20), (1.5, 0.25), (2.5, 0.20)],
}


def _componentes_do_defeito(
    tipo_defeito: str, severidade: float, rng: np.random.Generator
) -> list[Componente]:
    """Retorna as componentes espectrais do defeito, incluindo as dinâmicas e sub-harmônicos."""
    if tipo_defeito == "oil_whirl":
        ratio = rng.uniform(0.39, 0.48)
        return [Componente(ratio, 1.00), Componente(1.0, 0.25)]

    if tipo_defeito == "whirl_atrito":
        # Sem razão universal: faixa paramétrica marcada como hipótese (model_assumed).
        ratio = rng.uniform(0.30, 0.70)
        return [Componente(ratio, 1.00), Componente(1.0, 0.40)]

    componentes = list(DEFECT_PROFILES[tipo_defeito])
    if tipo_defeito == "rocamento" and severidade > 0.6:
        componentes += [Componente(o, p) for o, p in _SUB_HARMONICOS["rocamento"]]
    if tipo_defeito == "mancal_frouxo":
        componentes += [Componente(o, p) for o, p in _SUB_HARMONICOS["mancal_frouxo"]]
    return componentes


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

    `semente_fase` torna a fase das componentes determinística (referência de
    keyphasor estável por ponto de medição). O ruído permanece variável.
    """
    if tipo_defeito not in DEFECT_PROFILES:
        raise ValueError(f"tipo_defeito desconhecido: {tipo_defeito!r}")

    rng_ruido = rng if rng is not None else np.random.default_rng()
    rng_fase = np.random.default_rng(semente_fase) if semente_fase is not None else rng_ruido

    freq_rotacao_hz = rpm / 60.0
    t = np.arange(numero_amostras) / taxa_amostragem_hz
    sinal = np.zeros(numero_amostras)

    for componente in _componentes_do_defeito(tipo_defeito, severidade, rng_fase):
        freq = componente.ordem * freq_rotacao_hz
        amplitude = componente.peso * severidade
        fase = rng_fase.uniform(0, 2 * np.pi)
        sinal += amplitude * np.sin(2 * np.pi * freq * t + fase)
        if componente.sidebands_1x:
            for freq_lateral in (freq - freq_rotacao_hz, freq + freq_rotacao_hz):
                if freq_lateral > 0:
                    sinal += (amplitude * 0.2) * np.sin(
                        2 * np.pi * freq_lateral * t + rng_fase.uniform(0, 2 * np.pi)
                    )

    # Rub e folga elevam o piso de ruído (ver documento de assinaturas).
    ruido_efetivo = (
        max(ruido_fundo, 0.03) if tipo_defeito in {"rocamento", "mancal_frouxo"} else ruido_fundo
    )
    sinal += rng_ruido.normal(0, ruido_efetivo, numero_amostras)

    return sinal
