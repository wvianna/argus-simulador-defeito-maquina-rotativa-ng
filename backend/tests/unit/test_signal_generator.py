import numpy as np
import pytest

from app.domain import signal_generator as sg


def _freq_dominante(sinal: np.ndarray, taxa_amostragem_hz: float) -> float:
    n = len(sinal)
    freqs = np.fft.rfftfreq(n, d=1.0 / taxa_amostragem_hz)
    amplitudes = np.abs(np.fft.rfft(sinal))
    return float(freqs[np.argmax(amplitudes)])


@pytest.mark.parametrize("tipo_defeito", sorted(sg.TIPOS_DEFEITO_VALIDOS))
def test_gera_sinal_finito_para_todo_defeito(tipo_defeito: str) -> None:
    sinal = sg.generate_signal(
        rpm=1780.0,
        tipo_defeito=tipo_defeito,
        severidade=0.8,
        ruido_fundo=0.02,
        taxa_amostragem_hz=25_600.0,
        numero_amostras=8192,
        rng=np.random.default_rng(42),
    )
    assert sinal.shape == (8192,)
    assert np.isfinite(sinal).all()


ESTATICOS = [
    "sem_defeito",
    "desbalanceamento",
    "desalinhamento_angular",
    "desalinhamento_paralelo",
    "rocamento",
    "mancal_frouxo",
    "acoplamento_defeituoso",
    "rolamento_bpfo",
    "rolamento_bpfi",
    "rolamento_bsf",
    "rolamento_ftf",
]


@pytest.mark.parametrize("tipo_defeito", ESTATICOS)
def test_dominante_esta_na_assinatura_esperada(tipo_defeito: str) -> None:
    rpm = 1780.0
    taxa_amostragem_hz = 25_600.0
    numero_amostras = 8192
    sinal = sg.generate_signal(
        rpm=rpm,
        tipo_defeito=tipo_defeito,
        severidade=0.8,
        ruido_fundo=0.02,
        taxa_amostragem_hz=taxa_amostragem_hz,
        numero_amostras=numero_amostras,
        rng=np.random.default_rng(42),
    )

    freq_dominante = _freq_dominante(sinal, taxa_amostragem_hz)
    fr = rpm / 60.0
    resolucao = taxa_amostragem_hz / numero_amostras
    ordens = [c.ordem for c in sg.DEFECT_PROFILES[tipo_defeito]]

    assert any(abs(freq_dominante - o * fr) <= resolucao * 3 for o in ordens)


def test_oil_whirl_razao_entre_039_e_048() -> None:
    rpm = 3600.0
    taxa_amostragem_hz = 25_600.0
    sinal = sg.generate_signal(
        rpm=rpm,
        tipo_defeito="oil_whirl",
        severidade=0.7,
        ruido_fundo=0.02,
        taxa_amostragem_hz=taxa_amostragem_hz,
        numero_amostras=8192,
        rng=np.random.default_rng(7),
    )
    ordem = _freq_dominante(sinal, taxa_amostragem_hz) / (rpm / 60.0)
    assert 0.39 <= ordem <= 0.48


def test_whirl_atrito_e_subsincrono() -> None:
    rpm = 1780.0
    taxa_amostragem_hz = 25_600.0
    sinal = sg.generate_signal(
        rpm=rpm,
        tipo_defeito="whirl_atrito",
        severidade=0.7,
        ruido_fundo=0.02,
        taxa_amostragem_hz=taxa_amostragem_hz,
        numero_amostras=8192,
        rng=np.random.default_rng(7),
    )
    ordem = _freq_dominante(sinal, taxa_amostragem_hz) / (rpm / 60.0)
    assert 0.30 <= ordem <= 0.70
    assert ordem < 1.0  # whirl é não síncrono


def test_rocamento_severo_adiciona_sub_harmonicos() -> None:
    """Roçamento severo deve acrescentar sub-harmônicos (0,5X, 1/3X, 2/3X)."""
    rng = np.random.default_rng(42)

    ordens_leve = [c.ordem for c in sg._componentes_do_defeito("rocamento", 0.3, rng)]
    ordens_severo = [c.ordem for c in sg._componentes_do_defeito("rocamento", 0.9, rng)]

    assert not any(abs(o - 0.5) < 1e-9 for o in ordens_leve)
    assert any(abs(o - 0.5) < 1e-9 for o in ordens_severo)
    assert any(abs(o - 1 / 3) < 1e-9 for o in ordens_severo)
    assert any(abs(o - 2 / 3) < 1e-9 for o in ordens_severo)


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
            tipo_defeito="desbalanceamento",
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
