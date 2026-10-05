import "@testing-library/jest-dom/vitest";
import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "../App";
import ApprovalDialog from "../components/ApprovalDialog";
import CampaignDraft from "../components/CampaignDraft";
import type { CampaignDraftData, OperationPreview } from "../types";


const draft: CampaignDraftData = {
  draft_id: "draft-1",
  status: "paused",
  budget: "36.00",
  variants: {
    meta: [
      {
        angle: "Benefício direto",
        copy: { primary_text: "Texto", headline: "Oferta", description: "Acesso", cta: "Saiba mais" },
        creative_brief: "Produto em uso",
        validation_issues: [{ field: "headline", maximum: 40, actual: 41, message: "headline exceeds 40 characters" }],
      },
    ],
  },
};


describe("campaign workspace", () => {
  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  it("shows economics after a valid offer is submitted", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => draft,
    }));
    render(<App />);

    fireEvent.change(screen.getByLabelText("Nome da oferta"), { target: { value: "Curso Express" } });
    fireEvent.change(screen.getByLabelText("Preço"), { target: { value: "47" } });
    fireEvent.change(screen.getByLabelText("Margem bruta (%)"), { target: { value: "80" } });
    fireEvent.change(screen.getByLabelText("Conversão do checkout (%)"), { target: { value: "2" } });
    fireEvent.click(screen.getByRole("button", { name: "Gerar rascunho" }));

    expect(await screen.findByText("Rascunho pausado")).toBeInTheDocument();
    expect(screen.getByText("headline exceeds 40 characters")).toBeInTheDocument();
  });

  it("keeps approval disabled until a preview exists", () => {
    render(<ApprovalDialog preview={null} onApprove={vi.fn()} />);

    expect(screen.getByRole("button", { name: "Aprovar alteração" })).toBeDisabled();
  });

  it("prepares and approves a paused operation after the draft", async () => {
    const preview: OperationPreview = {
      operation_id: "op-1",
      token: "token-1",
      expires_at: "2026-10-04T23:59:00Z",
      payload_hash: "hash",
      summary: "Create paused meta campaign",
      status: "preview",
    };
    vi.stubGlobal("fetch", vi.fn()
      .mockResolvedValueOnce({ ok: true, json: async () => draft })
      .mockResolvedValueOnce({ ok: true, json: async () => preview })
      .mockResolvedValueOnce({ ok: true, json: async () => ({ operation_id: "op-1", status: "applied", campaign: { provider_id: "fake-1", platform: "meta", status: "paused" } }) }));
    render(<App />);

    fireEvent.change(screen.getByLabelText("Nome da oferta"), { target: { value: "Curso Express" } });
    fireEvent.click(screen.getByRole("button", { name: "Gerar rascunho" }));
    fireEvent.click(await screen.findByRole("button", { name: "Preparar prévia" }));
    expect(await screen.findByText("Create paused meta campaign")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Aprovar alteração" }));

    expect(await screen.findByText("Operação aplicada com campanha pausada.")).toBeInTheDocument();
  });
});
