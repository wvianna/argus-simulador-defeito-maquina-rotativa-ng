import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { FORMULARIO_INICIAL, validarFormulario } from "../domain/formularioSimulacao";
import { ChecklistValidacao } from "./ChecklistValidacao";

describe("validarFormulario", () => {
  it("é inválido quando ponto_id está vazio (CA-010)", () => {
    const estado = { ...FORMULARIO_INICIAL, ponto_id: "" };
    const { valido, payload } = validarFormulario(estado);
    expect(valido).toBe(false);
    expect(payload).toBeNull();
  });

  it("é válido com o ponto predefinido do formulário inicial", () => {
    const { valido, payload } = validarFormulario(FORMULARIO_INICIAL);
    expect(valido).toBe(true);
    expect(payload).not.toBeNull();
    expect(payload?.ponto_id).toBe("69c0eb95-618c-4fc7-a15f-e21f4abf7a99");
  });

  it("é válido quando todos os campos estão corretos", () => {
    const estado = { ...FORMULARIO_INICIAL, ponto_id: "11111111-1111-1111-1111-111111111111" };
    const { valido, payload } = validarFormulario(estado);
    expect(valido).toBe(true);
    expect(payload).not.toBeNull();
  });

  it("rejeita configuração que viole o critério de Nyquist (CA-011)", () => {
    const estado = {
      ...FORMULARIO_INICIAL,
      ponto_id: "11111111-1111-1111-1111-111111111111",
      taxa_amostragem_hz: "10",
    };
    const { valido } = validarFormulario(estado);
    expect(valido).toBe(false);
  });

  it("rejeita severidade fora do intervalo 0..1", () => {
    const estado = {
      ...FORMULARIO_INICIAL,
      ponto_id: "11111111-1111-1111-1111-111111111111",
      severidade: "1.5",
    };
    const { valido } = validarFormulario(estado);
    expect(valido).toBe(false);
  });

  it("rejeita limiar de picos fora do intervalo (FR-019)", () => {
    const estado = {
      ...FORMULARIO_INICIAL,
      ponto_id: "11111111-1111-1111-1111-111111111111",
      limiar_picos: "2",
    };
    const { valido } = validarFormulario(estado);
    expect(valido).toBe(false);
  });
});

describe("ChecklistValidacao", () => {
  it("renderiza um item por campo validado", () => {
    render(<ChecklistValidacao estado={FORMULARIO_INICIAL} />);
    const lista = screen.getByLabelText("checklist-validacao");
    expect(lista.querySelectorAll("li").length).toBeGreaterThan(0);
  });
});
