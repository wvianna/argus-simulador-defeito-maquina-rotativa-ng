import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

interface PainelSinalProps {
  sinalTempo: number[];
  taxaAmostragemHz: number;
  rmsTotal: number;
}

/** Painel visual: sinal simulado do acelerômetro + valor de RMS (FR-014). */
export function PainelSinal({ sinalTempo, taxaAmostragemHz, rmsTotal }: PainelSinalProps) {
  const dados = sinalTempo.map((valor, indice) => ({
    tempo: Number((indice / taxaAmostragemHz).toFixed(4)),
    amplitude: valor,
  }));

  return (
    <section aria-label="painel-sinal">
      <p>
        RMS total: <strong>{rmsTotal.toFixed(4)}</strong>
      </p>
      <div style={{ width: "100%", height: 250 }}>
        <ResponsiveContainer>
          <LineChart data={dados}>
            <XAxis dataKey="tempo" label={{ value: "Tempo (s)", position: "insideBottom", offset: -5 }} />
            <YAxis label={{ value: "Amplitude", angle: -90, position: "insideLeft" }} />
            <Tooltip />
            <Line type="monotone" dataKey="amplitude" dot={false} stroke="#16a34a" isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
