import type { SimulacaoRequest, SimulacaoResponse, SnapshotRequest, SnapshotResponse } from "../types/api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "/api";

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function post<TResponse>(path: string, body: unknown): Promise<TResponse> {
  const resposta = await fetch(`${API_BASE_URL}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => ({ detail: resposta.statusText }));
    throw new ApiError(corpo.detail ?? "Erro desconhecido", resposta.status);
  }

  return (await resposta.json()) as TResponse;
}

export function criarSimulacao(payload: SimulacaoRequest): Promise<SimulacaoResponse> {
  return post<SimulacaoResponse>("/simulacoes", payload);
}

export function criarSnapshot(payload: SnapshotRequest): Promise<SnapshotResponse> {
  return post<SnapshotResponse>("/snapshots", payload);
}
