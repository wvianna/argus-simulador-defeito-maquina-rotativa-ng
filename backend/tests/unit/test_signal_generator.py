import numpy as np
import pytest

from app.domain import signal_generator as sg


@pytest.mark.parametrize("tipo_defeito", sorted(sg.TIPOS_DEFEITO_VALIDOS - {"cavitacao"}))
def test_gera_sinal_com_dominante_esperada(tipo_defeito: str) -> None:
    rpm = 1780.0
    taxa_amostragem_hz = 25_600.0
    numero_amostras = 8192
    rng = np.random.default_rng(42)

    sinal = sg.generate_signal(
        rpm=rpm,
        tipo_defeito=tipo_defeito,
        severidade=0.8,
        ruido_fundo=0.02,
        taxa_amostragem_hz=taxa_amostragem_hz,
        numero_amostras=numero_amostras,
        rng=rng,
    )

    assert sinal.shape == (numero_amostras,)
    assert np.isfinite(sinal).all()

    # A frequência de maior amplitude no espectro deve corresponder a uma das
    # ordens configuradas no perfil do defeito (dentro de uma linha de resolução).
    freqs = np.fft.rfftfreq(numero_amostras, d=1.0 / taxa_amostragem_hz)
    amplitudes = np.abs(np.fft.rfft(sinal))
    freq_dominante = freqs[np.argmax(amplitudes)]

    freq_rotacao_hz = rpm / 60.0
    resolucao_hz = taxa_amostragem_hz / numero_amostras
    ordens_esperadas = [c.ordem for c in sg.DEFECT_PROFILES[tipo_defeito]]
    freqs_esperadas = [ordem * freq_rotacao_hz for ordem in ordens_esperadas]

    assert any(abs(freq_dominante - f) <= resolucao_hz * 3 for f in freqs_esperadas)


def test_cavitacao_eleva_piso_de_ruido() -> None:
    rng = np.random.default_rng(1)
    sinal = sg.generate_signal(
        rpm=1780.0,
        tipo_defeito="cavitacao",
        severidade=0.5,
        ruido_fundo=0.01,
        taxa_amostragem_hz=10_000.0,
        numero_amostras=4096,
        rng=rng,
    )
    assert np.std(sinal) > 0.1  # piso de ruído elevado, mesmo com ruido_fundo baixo


def test_tipo_defeito_invalido_levanta_erro() -> None:
    with pytest.raises(ValueError, match="tipo_defeito desconhecido"):
        sg.generate_signal(
            rpm=1780.0,
            tipo_defeito="inexistente",
            severidade=0.5,
            ruido_fundo=0.01,
            taxa_amostragem_hz=10_000.0,
            numero_amostras=1024,
        )


def test_semente_fase_produz_picos_estaveis_entre_leituras() -> None:
    """Regressão para FR-009: mesma referência de fase por ponto permite descarte."""
    from app.domain.fft_processor import calcular_picos
    from app.domain.signal_generator import generate_signal

    def _pico_dominante() -> float:
        sinal = generate_signal(
            rpm=1780.0,
            tipo_defeito="desbalanceamento_estatico",
            severidade=0.6,
            ruido_fundo=0.001,  # ruído mínimo para variar levemente a amplitude
            taxa_amostragem_hz=25_600.0,
            numero_amostras=8192,
            semente_fase=12345,
        )
        picos = calcular_picos(sinal, 25_600.0)
        return picos[0].fase_graus if picos else float("nan")

    f1, f2 = _pico_dominante(), _pico_dominante()
    assert abs(f1 - f2) < 1.0  # fase estável entre leituras do mesmo ponto
