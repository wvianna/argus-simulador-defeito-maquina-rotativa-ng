import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Help } from "./Help";

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
    <section className="panel panel--signal" aria-label="painel-sinal">
      <h2 className="panel-title">
        Sinal do acelerômetro <Help text="Sinal sintético no domínio do tempo (soma das componentes da assinatura do defeito + ruído) e valor de RMS total." />
      </h2>
      <p className="signal-rms">
        RMS total: <strong>{rmsTotal.toFixed(4)}</strong>
      </p>
      <div style={{ width: "100%", height: 180 }}>
        <ResponsiveContainer>
          <LineChart data={dados} margin={{ top: 8, right: 8, bottom: 8, left: 8 }}>
            <XAxis
              dataKey="tempo"
              tick={{ fill: "#7b9590", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
            />
            <YAxis tick={{ fill: "#7b9590", fontSize: 10 }} axisLine={false} tickLine={false} />
            <Tooltip
              contentStyle={{
                background: "#101a20",
                border: "1px solid rgba(61,214,192,0.3)",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ color: "#7b9590" }}
            />
            <Line
              type="monotone"
              dataKey="amplitude"
              dot={false}
              stroke="#3dd6c0"
              strokeWidth={1.5}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
