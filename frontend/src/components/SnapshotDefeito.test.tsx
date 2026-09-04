import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { SnapshotDefeito } from "./SnapshotDefeito";

describe("SnapshotDefeito", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async () =>
        new Response(JSON.stringify({ snapshot_id: "abc-123", criado_em: "2026-09-04T12:00:00Z" }), {
          status: 201,
        }),
      ),
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("dispara a chamada de snapshot com os dados corretos (CA-009)", async () => {
    const user = userEvent.setup();
    render(
      <SnapshotDefeito leituraId="leitura-1" leituraTipo="persistida" tipoDefeito="desbalanceamento_estatico" />,
    );

    await user.type(screen.getByLabelText(/Sensor/), "SENSOR-01");
    await user.click(screen.getByRole("button", { name: /Registrar snapshot/i }));

    await waitFor(() => expect(screen.getByRole("status")).toBeInTheDocument());
    expect(fetch).toHaveBeenCalledWith(
      expect.stringContaining("/snapshots"),
      expect.objectContaining({
        method: "POST",
        body: JSON.stringify({
          leitura_id: "leitura-1",
          leitura_tipo: "persistida",
          sensor_id: "SENSOR-01",
          tipo_defeito: "desbalanceamento_estatico",
        }),
      }),
    );
  });
});
