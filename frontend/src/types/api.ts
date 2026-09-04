// Tipos que espelham o contrato de POST /simulacoes e /snapshots (ver design.md)

export const TIPOS_DEFEITO = [
  "desbalanceamento_estatico",
  "desbalanceamento_acoplamento",
  "desbalanceamento_dinamico",
  "desalinhamento_angular",
  "desalinhamento_paralelo",
  "folga_tipo_a",
  "folga_tipo_b_c",
  "oil_whirl",
  "oil_whip",
  "rotor_rub",
  "desgaste_rolamento_bpfo",
  "desgaste_rolamento_bpfi",
  "desgaste_rolamento_bsf",
  "desgaste_rolamento_ftf",
  "cavitacao",
  "erro_sensor",
] as const;

export type TipoDefeito = (typeof TIPOS_DEFEITO)[number];

export interface SimulacaoRequest {
  ponto_id: string;
  rpm: number;
  tipo_defeito: TipoDefeito;
  severidade: number;
  ruido_fundo: number;
  taxa_amostragem_hz: number;
  numero_amostras: number;
  limiar_picos: number;
}

export interface Pico {
  frequencia_hz: number;
  amplitude: number;
  fase_graus: number;
}

export interface SimulacaoResponse {
  leitura_id: string;
  leitura_tipo: "persistida" | "trash";
  sinal_tempo: number[];
  taxa_amostragem_hz: number;
  limiar_picos: number;
  limiar_amplitude: number;
  picos_r3: Pico[];
  rms_total: number;
  rms_ruido: number;
  rms_picos: number;
  valor_dc: number;
  rotacao: number;
  descartada: boolean;
  motivo_descarte: string;
  tempo_processamento_ms: number;
  taxa_descarte_acumulada: number;
}

export interface SnapshotRequest {
  leitura_id: string;
  leitura_tipo: "persistida" | "trash";
  sensor_id: string;
  tipo_defeito: TipoDefeito;
}

export interface SnapshotResponse {
  snapshot_id: string;
  criado_em: string;
}
