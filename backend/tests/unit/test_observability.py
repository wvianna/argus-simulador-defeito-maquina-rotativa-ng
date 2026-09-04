import json

from app.observability.logging import calcular_taxa_descarte, log_simulacao


def test_log_simulacao_gera_json_valido(caplog) -> None:
    with caplog.at_level("INFO", logger="argus"):
        log_simulacao(ponto_id="abc-123", decisao="descartar", tempo_processamento_ms=12.345)

    assert len(caplog.records) == 1
    payload = json.loads(caplog.records[0].message)
    assert payload["evento"] == "simulacao_processada"
    assert payload["ponto_id"] == "abc-123"
    assert payload["decisao"] == "descartar"
    assert payload["tempo_processamento_ms"] == 12.345
    assert "timestamp" in payload


def test_calcular_taxa_descarte() -> None:
    assert calcular_taxa_descarte(total_descartadas=3, total_avaliadas=4) == 0.75
    assert calcular_taxa_descarte(total_descartadas=0, total_avaliadas=0) == 0.0
