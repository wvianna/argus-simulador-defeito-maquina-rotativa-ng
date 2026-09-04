import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { IndicadoresSimulacao } from "./IndicadoresSimulacao";

describe("IndicadoresSimulacao", () => {
  it("exibe tempo de processamento e taxa de descarte (CA-012)", () => {
    render(
      <IndicadoresSimulacao
        tempoProcessamentoMs={42.567}
        taxaDescarteAcumulada={0.734}
        descartada={false}
        motivoDescarte="Primeira leitura do ponto"
      />,
    );

    expect(screen.getByText("42.57 ms")).toBeInTheDocument();
    expect(screen.getByText("73.4%")).toBeInTheDocument();
    expect(screen.getByText(/Persistida/)).toBeInTheDocument();
  });
});
