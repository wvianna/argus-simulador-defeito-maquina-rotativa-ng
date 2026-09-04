import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { GraficoFFT } from "./GraficoFFT";

describe("GraficoFFT", () => {
  it("renderiza o container do gráfico com os picos fornecidos (CA-008)", () => {
    const picos = [
      { frequencia_hz: 29.7, amplitude: 3.2, fase_graus: 10 },
      { frequencia_hz: 59.4, amplitude: 0.8, fase_graus: 20 },
    ];
    render(<GraficoFFT picos={picos} threshold={2.5} rotacaoHz={30} />);
    expect(screen.getByLabelText("grafico-fft")).toBeInTheDocument();
  });

  it("exibe a rotação em Hz abaixo do gráfico", () => {
    render(<GraficoFFT picos={[]} threshold={1} rotacaoHz={30} />);
    expect(screen.getByLabelText("rotacao-hz")).toHaveTextContent("30.00 Hz");
  });
});
