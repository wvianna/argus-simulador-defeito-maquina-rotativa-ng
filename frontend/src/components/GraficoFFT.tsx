import {
  Bar,
  BarChart,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Pico } from "../types/api";
import { Help } from "./Help";

interface GraficoFFTProps {
  picos: Pico[];
  threshold: number;
  rotacaoHz: number;
}

interface TickProps {
  x?: number;
  y?: number;
  payload?: { value?: number | string };
}

/** Tick do eixo X com a frequência em Hz e a ordem normalizada (N = freq / rotação em Hz). */
function OrdinalTick({ x, y, payload, rotacaoHz }: TickProps & { rotacaoHz: number }) {
  const freq = Number(payload?.value ?? 0);
  const ordem = rotacaoHz > 0 ? freq / rotacaoHz : 0;
  return (
    <g transform={`translate(${x ?? 0},${y ?? 0})`}>
      <text dy={10} textAnchor="middle" fill="#a8c2bc" fontSize={11}>
        {freq.toFixed(1)}Hz
      </text>
      <text dy={24} textAnchor="middle" fill="#5d7a75" fontSize={10}>
        {ordem.toFixed(1)}N
      </text>
    </g>
  );
}

/** Gráfico de FFT: barras por frequência (com ordem N) + linha de threshold (FR-015). */
export function GraficoFFT({ picos, threshold, rotacaoHz }: GraficoFFTProps) {
  const dados = picos
    .slice()
    .sort((a, b) => a.frequencia_hz - b.frequencia_hz)
    .map((pico) => ({
      frequencia: Number(pico.frequencia_hz.toFixed(1)),
      ordem: rotacaoHz > 0 ? pico.frequencia_hz / rotacaoHz : 0,
      amplitude: pico.amplitude,
    }));

  const maxAmplitude = Math.max(0, ...dados.map((d) => d.amplitude));
  // Garante que a linha de threshold (limiar de alarme) fique dentro do eixo Y,
  // mesmo quando o maior pico for menor que o threshold.
  const limiteY = Math.max(maxAmplitude, threshold) * 1.15 || 1;

  return (
    <section className="panel panel--fft">
      <h2 className="panel-title">
        Espectro de frequência (FFT) <Help text="Transformada de Fourier do sinal. Cada barra é um pico na frequência indicada, com a ordem N (frequência ÷ rotação em Hz); a linha tracejada vermelha é o limiar que separa pico de ruído." />
      </h2>
      <div aria-label="grafico-fft" style={{ width: "100%", height: 210 }}>
        <ResponsiveContainer>
          <BarChart data={dados} margin={{ top: 16, right: 16, bottom: 34, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#1a2a31" />
            <XAxis
              dataKey="frequencia"
              tick={(props) => <OrdinalTick {...(props as TickProps)} rotacaoHz={rotacaoHz} />}
              axisLine={{ stroke: "#2b3b42" }}
              tickLine={false}
              label={{ value: "Frequência (Hz) · ordem N", position: "insideBottom", offset: -22, fill: "#7b9590", fontSize: 11 }}
            />
            <YAxis
              domain={[0, limiteY]}
              tick={{ fill: "#7b9590", fontSize: 10 }}
              axisLine={false}
              tickLine={false}
              label={{ value: "Amplitude", angle: -90, position: "insideLeft", fill: "#7b9590", fontSize: 11 }}
            />
            <Tooltip
              contentStyle={{
                background: "#101a20",
                border: "1px solid rgba(61,214,192,0.3)",
                borderRadius: 8,
                fontSize: 12,
              }}
              labelStyle={{ color: "#a8c2bc" }}
              labelFormatter={(label) => {
                const ordem = rotacaoHz > 0 ? Number(label) / rotacaoHz : 0;
                return `${label} Hz (${ordem.toFixed(1)}N)`;
              }}
            />
            <Bar dataKey="amplitude" fill="#3dd6c0" barSize={5} />
            <ReferenceLine
              y={threshold}
              stroke="#ff6b6b"
              strokeDasharray="4 4"
              label={{ value: "Limiar", fill: "#ff6b6b", fontSize: 11 }}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p className="fft-foot" aria-label="rotacao-hz">
        Rotação: <strong>{rotacaoHz.toFixed(2)} Hz</strong> (ordem N = frequência do pico ÷ rotação
        em Hz — ex.: 1N = 1× a rotação, 0.5N = meia rotação).
      </p>
    </section>
  );
}

