import { useState } from "react";
import { criarSimulacao, ApiError } from "../api/client";
import { FORMULARIO_INICIAL, validarFormulario, type FormularioState } from "../domain/formularioSimulacao";
import type { SimulacaoResponse } from "../types/api";
import { TIPOS_DEFEITO } from "../types/api";
import { ChecklistValidacao } from "./ChecklistValidacao";
import { GraficoFFT } from "./GraficoFFT";
import { Help } from "./Help";
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

  // Linha de limiar do gráfico: usa o limiar absoluto calculado no back-end (FR-019),
  // que descarta picos abaixo do valor configurado (ruído de fundo).
  const thresholdEstimado = resultado ? resultado.limiar_amplitude : 0;

  return (
    <div className="app">
      <header className="app-header reveal">
        <div className="brand">
          <span className="brand-mark">◆</span>
          <div>
            <h1 className="brand-title">ARGUS</h1>
            <p className="brand-sub">Simulador de Defeito de Máquina Rotativa</p>
          </div>
        </div>
        <span className="status">
          <span className="status-dot" /> online
        </span>
      </header>

      <form
        className="panel form-panel reveal"
        onSubmit={(e) => {
          e.preventDefault();
          void executarSimulacao();
        }}
      >
        <h2 className="panel-title">Parâmetros de simulação</h2>

        <div className="field-grid">
          <label className="field">
            <span>
              Ponto (UUID) <Help text="Identificador (UUID) do ponto de medição na hierarquia Planta &gt; Área &gt; Máquina &gt; Ponto. Use um Ponto já cadastrado (o start.sh cria um Ponto demo)." />
            </span>
            <input
              value={estado.ponto_id}
              onChange={(e) => atualizarCampo("ponto_id", e.target.value)}
            />
          </label>
          <label className="field">
            <span>
              RPM <Help text="Velocidade de rotação do eixo. A frequência de rotação é fr = RPM / 60 e define as ordens espectrais (1X, 2X, ...)." />
            </span>
            <input
              type="number"
              value={estado.rpm}
              onChange={(e) => atualizarCampo("rpm", e.target.value)}
            />
          </label>
          <label className="field">
            <span>
              Tipo de defeito <Help text="Falha simulada. Cada tipo gera uma assinatura espectral característica (ordens e amplitudes relativas) — ex.: desbalanceamento = 1X dominante." />
            </span>
            <select
              value={estado.tipo_defeito}
              onChange={(e) => atualizarCampo("tipo_defeito", e.target.value)}
            >
              {TIPOS_DEFEITO.map((tipo) => (
                <option key={tipo} value={tipo}>
                  {tipo}
                </option>
              ))}
            </select>
          </label>
          <label className="field">
            <span>
              Severidade (0 a 1) <Help text="Intensidade do defeito: 0–0.1 saudável/incipiente; 0.3–0.6 moderada; 0.6–0.8 severa; 0.8–1.0 crítica. Escala as amplitudes da assinatura." />
            </span>
            <input
              type="number"
              step="0.1"
              value={estado.severidade}
              onChange={(e) => atualizarCampo("severidade", e.target.value)}
            />
          </label>
          <label className="field">
            <span>
              Ruído de fundo <Help text="Nível de ruído aditivo (desvio padrão) somado ao sinal, simulando interferências de uma medição real." />
            </span>
            <input
              type="number"
              step="0.01"
              value={estado.ruido_fundo}
              onChange={(e) => atualizarCampo("ruido_fundo", e.target.value)}
            />
          </label>
          <label className="field">
            <span>
              Taxa de amostragem (Hz) <Help text="Frequência de amostragem do sinal. Deve ser maior que 2× a maior frequência de interesse (critério de Nyquist) — o checklist valida isso." />
            </span>
            <input
              type="number"
              value={estado.taxa_amostragem_hz}
              onChange={(e) => atualizarCampo("taxa_amostragem_hz", e.target.value)}
            />
          </label>
          <label className="field">
            <span>
              Número de amostras <Help text="Quantidade de pontos do sinal no tempo. Define a resolução espectral Δf = fs / N (quanto mais pontos, mais fina a resolução)." />
            </span>
            <input
              type="number"
              value={estado.numero_amostras}
              onChange={(e) => atualizarCampo("numero_amostras", e.target.value)}
            />
          </label>
          <label className="field">
            <span>
              Limiar de ruído ({Number(estado.limiar_picos) * 100}%) <Help text="Limiar relativo de detecção de picos na FFT. Picos abaixo deste valor são tratados como ruído de fundo e não aparecem no espectro." />
            </span>
            <input
              type="range"
              min="0.005"
              max="0.5"
              step="0.005"
              value={estado.limiar_picos}
              onChange={(e) => atualizarCampo("limiar_picos", e.target.value)}
            />
          </label>
        </div>

        <div className="form-actions">
          <ChecklistValidacao estado={estado} />
          <span className="form-actions-submit">
            <Help text="Gera o sinal sintético, calcula a FFT, aplica o descarte por tolerância e mostra sinal/espectro/indicadores." />
            <button className="btn btn--primary" type="submit" disabled={!valido || carregando}>
              {carregando ? "Simulando…" : "▶ Simular"}
            </button>
          </span>
        </div>
      </form>

      {erro && (
        <p role="alert" className="alert">
          {erro}
        </p>
      )}

      {resultado && (
        <div className="results">
          <div className="results-row">
            <PainelSinal
              sinalTempo={resultado.sinal_tempo}
              taxaAmostragemHz={resultado.taxa_amostragem_hz}
              rmsTotal={resultado.rms_total}
            />
            <GraficoFFT
              picos={resultado.picos_r3}
              threshold={thresholdEstimado}
              rotacaoHz={resultado.rotacao / 60}
            />
          </div>
          <div className="results-bottom">
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
          </div>
        </div>
      )}
    </div>
  );
}

