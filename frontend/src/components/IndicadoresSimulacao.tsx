import { Help } from "./Help";

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
    <section className="panel panel--metrics">
      <h2 className="panel-title">
        Telemetria <Help text="Medidas da execução: tempo de processamento, taxa de descarte acumulada e o resultado da leitura (persistida como referência ou descartada como redundante)." />
      </h2>
      <dl className="metrics" aria-label="indicadores-simulacao">
        <div className="metric">
          <dt>Tempo de processamento</dt>
          <dd>{tempoProcessamentoMs.toFixed(2)} ms</dd>
        </div>
        <div className="metric">
          <dt>Taxa de descarte acumulada</dt>
          <dd>{(taxaDescarteAcumulada * 100).toFixed(1)}%</dd>
        </div>
        <div className="metric metric--verdict">
          <dt>Resultado desta leitura</dt>
          <dd>
            {descartada ? "Descartada" : "Persistida"} — {motivoDescarte}
          </dd>
        </div>
      </dl>
    </section>
  );
}
