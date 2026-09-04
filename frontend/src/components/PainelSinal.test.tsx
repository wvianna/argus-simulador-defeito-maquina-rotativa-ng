import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { PainelSinal } from "./PainelSinal";

describe("PainelSinal", () => {
  it("exibe o RMS total e o gráfico do sinal (CA-008)", () => {
    render(<PainelSinal sinalTempo={[0, 1, -1, 0.5]} taxaAmostragemHz={1000} rmsTotal={1.234} />);
    expect(screen.getByLabelText("painel-sinal")).toBeInTheDocument();
    expect(screen.getByText(/1\.2340/)).toBeInTheDocument();
  });
});
