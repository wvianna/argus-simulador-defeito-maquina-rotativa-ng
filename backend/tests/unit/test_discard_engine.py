from app.domain.discard_engine import (
    DecisaoDescarte,
    LeituraAvaliar,
    Tolerancias,
    avaliar,
)
from app.domain.fft_processor import Pico

TOLERANCIAS = Tolerancias(
    desvio_rotacao=5.0, delta_frequencia_hz=0.5, delta_amplitude=0.1, delta_fase_graus=15.0
)


def test_primeira_leitura_do_ponto_e_sempre_persistida() -> None:
    leitura = LeituraAvaliar(rotacao=1780.0, picos=[Pico(29.7, 3.0, 0.0)])

    resultado = avaliar(leitura, ultima_persistida=None, tolerancias=TOLERANCIAS)

    assert resultado.persistir is True
    assert resultado.decisao is DecisaoDescarte.PERSISTIR_PRIMEIRA_LEITURA


def test_regra_de_ouro_persiste_sem_checar_r3() -> None:
    ultima = LeituraAvaliar(rotacao=1780.0, picos=[Pico(29.7, 3.0, 0.0)])
    atual = LeituraAvaliar(rotacao=1795.0, picos=[Pico(1000.0, 50.0, 90.0)])  # pico bem diferente

    resultado = avaliar(atual, ultima, TOLERANCIAS)

    assert resultado.persistir is True
    assert resultado.decisao is DecisaoDescarte.PERSISTIR_REGRA_DE_OURO


def test_picos_dentro_da_tolerancia_sao_descartados() -> None:
    ultima = LeituraAvaliar(rotacao=1780.0, picos=[Pico(29.7, 3.0, 10.0)])
    atual = LeituraAvaliar(rotacao=1781.0, picos=[Pico(29.8, 3.05, 12.0)])

    resultado = avaliar(atual, ultima, TOLERANCIAS)

    assert resultado.persistir is False
    assert resultado.decisao is DecisaoDescarte.DESCARTAR


def test_pico_fora_da_tolerancia_e_persistido_e_vira_referencia() -> None:
    ultima = LeituraAvaliar(rotacao=1780.0, picos=[Pico(29.7, 3.0, 10.0)])
    atual = LeituraAvaliar(rotacao=1781.0, picos=[Pico(29.7, 8.0, 10.0)])  # amplitude muito maior

    resultado = avaliar(atual, ultima, TOLERANCIAS)

    assert resultado.persistir is True
    assert resultado.decisao is DecisaoDescarte.PERSISTIR_FORA_TOLERANCIA


def test_comparacao_usa_ultima_persistida_nao_a_ultima_avaliada() -> None:
    # Regressão para FR-008: mesmo que uma leitura intermediária tenha sido
    # descartada, a próxima avaliação deve comparar contra a última PERSISTIDA.
    ultima_persistida = LeituraAvaliar(rotacao=1780.0, picos=[Pico(29.7, 3.0, 10.0)])

    # Simula que uma leitura anterior foi descartada (não usada como referência).
    leitura_descartada = LeituraAvaliar(rotacao=1780.2, picos=[Pico(29.75, 3.02, 10.5)])
    resultado_intermediario = avaliar(leitura_descartada, ultima_persistida, TOLERANCIAS)
    assert resultado_intermediario.persistir is False

    # A leitura seguinte deve ser comparada contra ultima_persistida, não contra leitura_descartada.
    proxima_leitura = LeituraAvaliar(rotacao=1780.3, picos=[Pico(29.78, 3.03, 10.8)])
    resultado_final = avaliar(proxima_leitura, ultima_persistida, TOLERANCIAS)
    assert resultado_final.persistir is False
