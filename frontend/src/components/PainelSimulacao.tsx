import { useState } from "react";
import { criarSimulacao, ApiError } from "../api/client";
import { FORMULARIO_INICIAL, validarFormulario, type FormularioState } from "../domain/formularioSimulacao";
import type { SimulacaoResponse } from "../types/api";
import { TIPOS_DEFEITO } from "../types/api";
import { ChecklistValidacao } from "./ChecklistValidacao";
import { GraficoFFT } from "./GraficoFFT";
import { IndicadoresSimulacao } from "./IndicadoresSimulacao";
import { PainelSinal } from "./PainelSinal";
import { SnapshotDefeito } from "./SnapshotDefeito";

/** Painel principal: formulário, checklist, disparo da simulação e resultados (FR-014 a FR-018). */
export function PainelSimulacao() {
  const [estado, setEstado] = useState<FormularioState>(FORMULARIO_INICIAL);
  const [resultado, setResultado] = useState<SimulacaoResponse | null>(null);
  const [erro, setErro] = useState<string | null>(null);
  const [carregando, setCarregando] = useState(false);

  const { valido, payload } = validarFormulario(estado);

  function atualizarCampo<K extends keyof FormularioState>(campo: K, valor: FormularioState[K]) {
    setEstado((atual) => ({ ...atual, [campo]: valor }));
  }

  async function executarSimulacao() {
    if (!payload) return;
    setCarregando(true);
    setErro(null);
    try {
      const resposta = await criarSimulacao(payload);
      setResultado(resposta);
    } catch (e) {
      setErro(e instanceof ApiError ? e.message : "Erro inesperado ao simular");
      setResultado(null);
    } finally {
      setCarregando(false);
    }
  }

  // Limiar de alarme (placeholder do MVP): 80% da maior amplitude dos picos,
  // para a linha de threshold ficar dentro da escala visível do gráfico de FFT.
  const thresholdEstimado = resultado
    ? Math.max(...resultado.picos_r3.map((p) => p.amplitude), 0) * 0.8
    : 0;

  return (
    <main>
      <h1>Argus — Simulador de Defeito de Máquina Rotativa</h1>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          void executarSimulacao();
        }}
      >
        <label>
          Ponto (UUID)
          <input value={estado.ponto_id} onChange={(e) => atualizarCampo("ponto_id", e.target.value)} />
        </label>
        <label>
          RPM
          <input type="number" value={estado.rpm} onChange={(e) => atualizarCampo("rpm", e.target.value)} />
        </label>
        <label>
          Tipo de defeito
          <select value={estado.tipo_defeito} onChange={(e) => atualizarCampo("tipo_defeito", e.target.value)}>
            {TIPOS_DEFEITO.map((tipo) => (
              <option key={tipo} value={tipo}>
                {tipo}
              </option>
            ))}
          </select>
        </label>
        <label>
          Severidade (0 a 1)
          <input
            type="number"
            step="0.1"
            value={estado.severidade}
            onChange={(e) => atualizarCampo("severidade", e.target.value)}
          />
        </label>
        <label>
          Ruído de fundo
          <input
            type="number"
            step="0.01"
            value={estado.ruido_fundo}
            onChange={(e) => atualizarCampo("ruido_fundo", e.target.value)}
          />
        </label>
        <label>
          Taxa de amostragem (Hz)
          <input
            type="number"
            value={estado.taxa_amostragem_hz}
            onChange={(e) => atualizarCampo("taxa_amostragem_hz", e.target.value)}
          />
        </label>
        <label>
          Número de amostras
          <input
            type="number"
            value={estado.numero_amostras}
            onChange={(e) => atualizarCampo("numero_amostras", e.target.value)}
          />
        </label>

        <ChecklistValidacao estado={estado} />

        <button type="submit" disabled={!valido || carregando}>
          {carregando ? "Simulando..." : "Simular"}
        </button>
      </form>

      {erro && <p role="alert">{erro}</p>}

      {resultado && (
        <>
          <PainelSinal
            sinalTempo={resultado.sinal_tempo}
            taxaAmostragemHz={resultado.taxa_amostragem_hz}
            rmsTotal={resultado.rms_total}
          />
          <GraficoFFT picos={resultado.picos_r3} threshold={thresholdEstimado} />
          <IndicadoresSimulacao
            tempoProcessamentoMs={resultado.tempo_processamento_ms}
            taxaDescarteAcumulada={resultado.taxa_descarte_acumulada}
            descartada={resultado.descartada}
            motivoDescarte={resultado.motivo_descarte}
          />
          <SnapshotDefeito
            leituraId={resultado.leitura_id}
            leituraTipo={resultado.leitura_tipo}
            tipoDefeito={estado.tipo_defeito as (typeof TIPOS_DEFEITO)[number]}
          />
        </>
      )}
    </main>
  );
}
