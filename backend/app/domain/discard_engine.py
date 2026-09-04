"""Motor de descarte: regra de ouro + Paralelepípedo de Descarte (FR-007 a FR-011)."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from .fft_processor import Pico


class DecisaoDescarte(StrEnum):
    PERSISTIR_PRIMEIRA_LEITURA = "persistir_primeira_leitura"
    PERSISTIR_REGRA_DE_OURO = "persistir_regra_de_ouro"
    PERSISTIR_FORA_TOLERANCIA = "persistir_fora_tolerancia"
    DESCARTAR = "descartar"


@dataclass(frozen=True)
class Tolerancias:
    desvio_rotacao: float
    delta_frequencia_hz: float
    delta_amplitude: float
    delta_fase_graus: float


@dataclass(frozen=True)
class LeituraAvaliar:
    rotacao: float
    picos: list[Pico]


@dataclass(frozen=True)
class ResultadoAvaliacao:
    decisao: DecisaoDescarte
    persistir: bool
    motivo: str


def _pico_mais_proximo(pico: Pico, referencia: list[Pico]) -> Pico | None:
    if not referencia:
        return None
    return min(referencia, key=lambda p: abs(p.frequencia_hz - pico.frequencia_hz))


def _fora_da_tolerancia(pico: Pico, referencia: Pico, tolerancias: Tolerancias) -> bool:
    return (
        abs(pico.frequencia_hz - referencia.frequencia_hz) > tolerancias.delta_frequencia_hz
        or abs(pico.amplitude - referencia.amplitude) > tolerancias.delta_amplitude
        or abs(pico.fase_graus - referencia.fase_graus) > tolerancias.delta_fase_graus
    )


def avaliar(
    leitura_atual: LeituraAvaliar,
    ultima_persistida: LeituraAvaliar | None,
    tolerancias: Tolerancias,
) -> ResultadoAvaliacao:
    """Aplica a regra de ouro e, se necessário, o Paralelepípedo de Descarte (R^3).

    A comparação é sempre feita contra a última leitura efetivamente persistida,
    nunca contra a última leitura avaliada/descartada (FR-008).
    """
    if ultima_persistida is None:
        return ResultadoAvaliacao(
            DecisaoDescarte.PERSISTIR_PRIMEIRA_LEITURA, True, "Primeira leitura do ponto"
        )

    variacao_rotacao = abs(leitura_atual.rotacao - ultima_persistida.rotacao)
    if variacao_rotacao > tolerancias.desvio_rotacao and len(leitura_atual.picos) > 0:
        return ResultadoAvaliacao(
            DecisaoDescarte.PERSISTIR_REGRA_DE_OURO,
            True,
            f"Variação de rotação {variacao_rotacao} > desvio {tolerancias.desvio_rotacao}",
        )

    for pico in leitura_atual.picos:
        referencia = _pico_mais_proximo(pico, ultima_persistida.picos)
        if referencia is None or _fora_da_tolerancia(pico, referencia, tolerancias):
            return ResultadoAvaliacao(
                DecisaoDescarte.PERSISTIR_FORA_TOLERANCIA,
                True,
                f"Pico {pico.frequencia_hz:.2f}Hz fora da tolerância R^3",
            )

    return ResultadoAvaliacao(
        DecisaoDescarte.DESCARTAR, False, "Todos os picos dentro da tolerância R^3"
    )
