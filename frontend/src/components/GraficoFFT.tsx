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
      <text dy={10} textAnchor="middle" fill="#94a3b8" fontSize={11}>
        {freq.toFixed(1)}Hz
      </text>
      <text dy={24} textAnchor="middle" fill="#64748b" fontSize={10}>
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
    <div>
      <div aria-label="grafico-fft" style={{ width: "100%", height: 320 }}>
        <ResponsiveContainer>
          <BarChart data={dados} margin={{ top: 16, right: 16, bottom: 34, left: 8 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="frequencia"
              tick={(props) => <OrdinalTick {...(props as TickProps)} rotacaoHz={rotacaoHz} />}
              label={{ value: "Frequência (Hz) · ordem N", position: "insideBottom", offset: -22 }}
            />
            <YAxis domain={[0, limiteY]} label={{ value: "Amplitude", angle: -90, position: "insideLeft" }} />
            <Tooltip
              labelFormatter={(label) => {
                const ordem = rotacaoHz > 0 ? Number(label) / rotacaoHz : 0;
                return `${label} Hz (${ordem.toFixed(1)}N)`;
              }}
            />
            <Bar dataKey="amplitude" fill="#2563eb" barSize={5} />
            <ReferenceLine y={threshold} stroke="red" strokeDasharray="4 4" label="Limiar" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <p aria-label="rotacao-hz">
        Rotação: <strong>{rotacaoHz.toFixed(2)} Hz</strong> (ordem N = frequência do pico ÷ rotação
        em Hz — ex.: 1N = 1× a rotação, 0.5N = meia rotação).
      </p>
    </div>
  );
}

