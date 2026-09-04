import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GraficoFFT } from "./GraficoFFT";

describe("GraficoFFT", () => {
  it("renderiza o container do gráfico com os picos fornecidos (CA-008)", () => {
    const picos = [
      { frequencia_hz: 29.7, amplitude: 3.2, fase_graus: 10 },
      { frequencia_hz: 59.4, amplitude: 0.8, fase_graus: 20 },
    ];
    render(<GraficoFFT picos={picos} threshold={2.5} />);
    expect(screen.getByLabelText("grafico-fft")).toBeInTheDocument();
  });
});
