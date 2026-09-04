import type { SimulacaoRequest } from "../types/api";
import { TIPOS_DEFEITO } from "../types/api";

export interface FormularioState {
  ponto_id: string;
  rpm: string;
  tipo_defeito: string;
  severidade: string;
  ruido_fundo: string;
  taxa_amostragem_hz: string;
  numero_amostras: string;
  limiar_picos: string;
}

export const FORMULARIO_INICIAL: FormularioState = {
  // Ponto demo criado pelo start.sh (hierarquia Planta>Área>Máquina>Ponto).
  ponto_id: "69c0eb95-618c-4fc7-a15f-e21f4abf7a99",
  rpm: "1780",
  tipo_defeito: TIPOS_DEFEITO[0],
  severidade: "0.6",
  ruido_fundo: "0.05",
  taxa_amostragem_hz: "25600",
  numero_amostras: "4096",
  limiar_picos: "0.05",
};

export interface ItemChecklist {
  chave: string;
  descricao: string;
  valido: boolean;
}

/** Valida o formulário de simulação e estima violação de Nyquist no cliente (espelha NFR-001). */
export function validarFormulario(estado: FormularioState): {
  itens: ItemChecklist[];
  valido: boolean;
  payload: SimulacaoRequest | null;
} {
  const rpm = Number(estado.rpm);
  const severidade = Number(estado.severidade);
  const ruidoFundo = Number(estado.ruido_fundo);
  const taxaAmostragemHz = Number(estado.taxa_amostragem_hz);
  const numeroAmostras = Number(estado.numero_amostras);
  const limiarPicos = Number(estado.limiar_picos);

  const fmaxEstimadoHz = (rpm / 60) * 20; // aproximação: 10x ordem padrão x margem de 2 (ver fft_processor.estimar_fmax_hz)

  const itens: ItemChecklist[] = [
    { chave: "ponto_id", descricao: "Ponto selecionado", valido: estado.ponto_id.trim().length > 0 },
    { chave: "rpm", descricao: "RPM maior que zero", valido: Number.isFinite(rpm) && rpm > 0 },
    {
      chave: "tipo_defeito",
      descricao: "Tipo de defeito válido",
      valido: (TIPOS_DEFEITO as readonly string[]).includes(estado.tipo_defeito),
    },
    {
      chave: "severidade",
      descricao: "Severidade entre 0 e 1",
      valido: Number.isFinite(severidade) && severidade >= 0 && severidade <= 1,
    },
    {
      chave: "ruido_fundo",
      descricao: "Ruído de fundo maior ou igual a zero",
      valido: Number.isFinite(ruidoFundo) && ruidoFundo >= 0,
    },
    {
      chave: "numero_amostras",
      descricao: "Número de amostras entre 1 e 65536",
      valido: Number.isInteger(numeroAmostras) && numeroAmostras > 0 && numeroAmostras <= 65536,
    },
    {
      chave: "limiar_picos",
      descricao: "Limiar de picos entre 0 e 1",
      valido: Number.isFinite(limiarPicos) && limiarPicos > 0 && limiarPicos <= 1,
    },
    {
      chave: "nyquist",
      descricao: "Taxa de amostragem respeita o critério de Nyquist (> 2x Fmax estimado)",
      valido: Number.isFinite(taxaAmostragemHz) && taxaAmostragemHz > 2 * fmaxEstimadoHz,
    },
  ];

  const valido = itens.every((item) => item.valido);

  return {
    itens,
    valido,
    payload: valido
      ? {
          ponto_id: estado.ponto_id,
          rpm,
          tipo_defeito: estado.tipo_defeito as SimulacaoRequest["tipo_defeito"],
          severidade,
          ruido_fundo: ruidoFundo,
          taxa_amostragem_hz: taxaAmostragemHz,
          numero_amostras: numeroAmostras,
          limiar_picos: limiarPicos,
        }
      : null,
  };
}
