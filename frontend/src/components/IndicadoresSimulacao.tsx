interface IndicadoresSimulacaoProps {
  tempoProcessamentoMs: number;
  taxaDescarteAcumulada: number;
  descartada: boolean;
  motivoDescarte: string;
}

/** Indicadores de tempo de processamento e taxa de descarte (FR-017, NFR-002, NFR-004). */
export function IndicadoresSimulacao({
  tempoProcessamentoMs,
  taxaDescarteAcumulada,
  descartada,
  motivoDescarte,
}: IndicadoresSimulacaoProps) {
  return (
    <dl aria-label="indicadores-simulacao">
      <dt>Tempo de processamento</dt>
      <dd>{tempoProcessamentoMs.toFixed(2)} ms</dd>

      <dt>Taxa de descarte acumulada</dt>
      <dd>{(taxaDescarteAcumulada * 100).toFixed(1)}%</dd>

      <dt>Resultado desta leitura</dt>
      <dd>
        {descartada ? "Descartada" : "Persistida"} — {motivoDescarte}
      </dd>
    </dl>
  );
}
