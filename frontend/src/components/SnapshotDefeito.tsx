import { useState } from "react";
import { criarSnapshot } from "../api/client";
import type { TipoDefeito } from "../types/api";
import { Help } from "./Help";

interface SnapshotDefeitoProps {
  leituraId: string;
  leituraTipo: "persistida" | "trash";
  tipoDefeito: TipoDefeito;
}

/** Ação de registrar snapshot de defeito (par sensor + anomalia) para treinamento/RCA (FR-016). */
export function SnapshotDefeito({ leituraId, leituraTipo, tipoDefeito }: SnapshotDefeitoProps) {
  const [sensorId, setSensorId] = useState("");
  const [status, setStatus] = useState<"idle" | "enviando" | "sucesso" | "erro">("idle");
  const [erro, setErro] = useState<string | null>(null);

  async function registrarSnapshot() {
    setStatus("enviando");
    setErro(null);
    try {
      await criarSnapshot({
        leitura_id: leituraId,
        leitura_tipo: leituraTipo,
        sensor_id: sensorId,
        tipo_defeito: tipoDefeito,
      });
      setStatus("sucesso");
    } catch (e) {
      setStatus("erro");
      setErro(e instanceof Error ? e.message : "Erro desconhecido");
    }
  }

  return (
    <section className="panel panel--snapshot" aria-label="snapshot-defeito">
      <h2 className="panel-title">
        Registrar snapshot de defeito <Help text="Grava o par sensor + anomalia associado à leitura gerada, para uso em treinamento e pesquisa de causa raiz (RCA)." />
      </h2>
      <div className="snapshot">
        <label className="field">
          <span>
            Sensor <Help text="Identificador do sensor que fez a medição (ex.: SENSOR-01)." />
          </span>
          <input value={sensorId} onChange={(e) => setSensorId(e.target.value)} placeholder="ID do sensor" />
        </label>
        <button
          className="btn"
          type="button"
          disabled={!sensorId || status === "enviando"}
          onClick={registrarSnapshot}
        >
          Registrar snapshot de defeito
        </button>
      </div>
      {status === "sucesso" && (
        <p className="snapshot-status" role="status">
          Snapshot registrado com sucesso.
        </p>
      )}
      {status === "erro" && <p role="alert">Falha ao registrar snapshot: {erro}</p>}
    </section>
  );
}
