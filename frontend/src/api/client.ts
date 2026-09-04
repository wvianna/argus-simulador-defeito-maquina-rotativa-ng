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

/** Extrai uma mensagem legível do corpo de erro da API (detail string ou array Pydantic). */
function mensagemDoErro(corpo: unknown, statusText: string): string {
  const detail = (corpo as { detail?: unknown } | null)?.detail;
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) {
    return detail
      .map((d) => {
        const msg = (d as { msg?: string }).msg;
        const loc = (d as { loc?: unknown[] }).loc;
        return msg ? `${Array.isArray(loc) ? loc.join(".") : "campo"}: ${msg}` : JSON.stringify(d);
      })
      .join(" | ");
  }
  return statusText || "Erro desconhecido";
}

async function post<TResponse>(path: string, body: unknown): Promise<TResponse> {
  let resposta: Response;
  try {
    resposta = await fetch(`${API_BASE_URL}${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
  } catch {
    throw new ApiError(
      "Não foi possível conectar ao servidor. Verifique se os serviços estão no ar (rode ./start.sh).",
      0,
    );
  }

  if (!resposta.ok) {
    const corpo = await resposta.json().catch(() => null);
    throw new ApiError(mensagemDoErro(corpo, resposta.statusText), resposta.status);
  }

  return (await resposta.json()) as TResponse;
}

export function criarSimulacao(payload: SimulacaoRequest): Promise<SimulacaoResponse> {
  return post<SimulacaoResponse>("/simulacoes", payload);
}

export function criarSnapshot(payload: SnapshotRequest): Promise<SnapshotResponse> {
  return post<SnapshotResponse>("/snapshots", payload);
}
