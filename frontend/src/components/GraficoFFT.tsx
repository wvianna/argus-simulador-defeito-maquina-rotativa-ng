import { Bar, BarChart, CartesianGrid, ReferenceLine, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import type { Pico } from "../types/api";

interface GraficoFFTProps {
  picos: Pico[];
  threshold: number;
}

/** Gráfico de FFT: barras por frequência + linha horizontal de threshold (FR-015). */
export function GraficoFFT({ picos, threshold }: GraficoFFTProps) {
  const dados = picos
    .slice()
    .sort((a, b) => a.frequencia_hz - b.frequencia_hz)
    .map((pico) => ({
      frequencia: Number(pico.frequencia_hz.toFixed(1)),
      amplitude: pico.amplitude,
    }));

  const maxAmplitude = Math.max(0, ...dados.map((d) => d.amplitude));
  // Garante que a linha de threshold (limiar de alarme) fique dentro do eixo Y,
  // mesmo quando o maior pico for menor que o threshold.
  const limiteY = Math.max(maxAmplitude, threshold) * 1.15 || 1;

  return (
    <div aria-label="grafico-fft" style={{ width: "100%", height: 300 }}>
      <ResponsiveContainer>
        <BarChart data={dados} margin={{ top: 16, right: 16, bottom: 16, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="frequencia" label={{ value: "Frequência (Hz)", position: "insideBottom", offset: -5 }} />
          <YAxis domain={[0, limiteY]} label={{ value: "Amplitude", angle: -90, position: "insideLeft" }} />
          <Tooltip />
          <Bar dataKey="amplitude" fill="#2563eb" barSize={28} />
          <ReferenceLine y={threshold} stroke="red" strokeDasharray="4 4" label="Limiar" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

