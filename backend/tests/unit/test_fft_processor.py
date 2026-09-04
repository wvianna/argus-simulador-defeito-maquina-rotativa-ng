import numpy as np
import pytest

from app.domain import fft_processor as fp


def _sinal_senoide(
    freq_hz: float, amplitude: float, taxa_amostragem_hz: float, numero_amostras: int
) -> np.ndarray:
    t = np.arange(numero_amostras) / taxa_amostragem_hz
    return amplitude * np.sin(2 * np.pi * freq_hz * t)


def test_calcular_picos_identifica_frequencia_conhecida() -> None:
    taxa_amostragem_hz = 10_000.0
    numero_amostras = 4096
    sinal = _sinal_senoide(200.0, 3.0, taxa_amostragem_hz, numero_amostras)

    picos = fp.calcular_picos(sinal, taxa_amostragem_hz)

    assert len(picos) >= 1
    pico_principal = max(picos, key=lambda p: p.amplitude)
    resolucao_hz = taxa_amostragem_hz / numero_amostras
    assert abs(pico_principal.frequencia_hz - 200.0) <= resolucao_hz
    assert pico_principal.amplitude == pytest.approx(3.0, rel=0.05)


def test_rms_picos_e_ruido_coerentes_com_rms_total() -> None:
    # Frequência escolhida para coincidir exatamente com um bin da FFT (sem leakage).
    taxa_amostragem_hz = 4096.0
    numero_amostras = 4096
    sinal = _sinal_senoide(200.0, 3.0, taxa_amostragem_hz, numero_amostras)

    resultado = fp.processar(sinal, taxa_amostragem_hz, fmax_hz=500.0)

    assert resultado.rms_total == pytest.approx(3.0 / np.sqrt(2), rel=0.05)
    assert resultado.rms_picos == pytest.approx(resultado.rms_total, rel=0.1)
    assert resultado.rms_ruido == pytest.approx(0.0, abs=0.2)
    assert resultado.valor_dc == pytest.approx(0.0, abs=1e-9)


def test_limiar_picos_descarta_ruido_de_fundo() -> None:
    """FR-019: limiar relativo maior deve reduzir a quantidade de picos detectados."""
    taxa_amostragem_hz = 10_000.0
    numero_amostras = 4096
    rng = np.random.default_rng(7)
    sinal = 3.0 * np.sin(2 * np.pi * 200.0 * np.arange(numero_amostras) / taxa_amostragem_hz)
    sinal += rng.normal(0, 0.4, numero_amostras)  # ruído de fundo significativo

    picos_baixo = fp.calcular_picos(sinal, taxa_amostragem_hz, limiar_relativo=0.001)
    picos_alto = fp.calcular_picos(sinal, taxa_amostragem_hz, limiar_relativo=0.5)

    assert len(picos_alto) <= len(picos_baixo)
    assert len(picos_alto) >= 1  # o pico dominante deve permanecer


def test_processar_retorna_limiar_absoluto() -> None:
    taxa_amostragem_hz = 4096.0
    numero_amostras = 4096
    sinal = _sinal_senoide(200.0, 3.0, taxa_amostragem_hz, numero_amostras)

    resultado = fp.processar(sinal, taxa_amostragem_hz, fmax_hz=500.0, limiar_relativo=0.1)

    amplitude_max = fp.amplitude_maxima(sinal, taxa_amostragem_hz)
    assert resultado.limiar_absoluto == pytest.approx(amplitude_max * 0.1)
    assert resultado.limiar_absoluto > 0


def test_validar_nyquist_rejeita_taxa_insuficiente() -> None:
    with pytest.raises(fp.NyquistViolationError):
        fp.validar_nyquist(taxa_amostragem_hz=800.0, fmax_hz=500.0)  # 800 <= 2*500


def test_validar_nyquist_aceita_taxa_suficiente() -> None:
    fp.validar_nyquist(taxa_amostragem_hz=1200.0, fmax_hz=500.0)  # 1200 > 1000, ok


def test_estimar_fmax_usa_ordem_maxima_do_perfil() -> None:
    # A ordem do perfil (5.4) é menor que ORDEM_MAXIMA_PADRAO (10.0), que atua como piso mínimo.
    fmax = fp.estimar_fmax_hz(rpm=1800.0, tipo_defeito="desgaste_rolamento_bpfi")
    freq_rotacao_hz = 1800.0 / 60.0
    assert fmax == pytest.approx(fp.ORDEM_MAXIMA_PADRAO * fp.MARGEM_SIDEBAND * freq_rotacao_hz)


def test_decimar_sinal_mantem_sinal_curto_intacto() -> None:
    sinal = np.arange(100, dtype=float)
    assert fp.decimar_sinal(sinal, max_pontos=2000) == list(sinal)


def test_decimar_sinal_reduz_sinal_longo() -> None:
    sinal = np.arange(10_000, dtype=float)
    resultado = fp.decimar_sinal(sinal, max_pontos=2000)
    assert len(resultado) <= 2000
