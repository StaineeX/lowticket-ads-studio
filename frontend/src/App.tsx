import { useState } from "react";
import { approveOperation, generateDraft, previewOperation } from "./api";
import ApprovalDialog from "./components/ApprovalDialog";
import CampaignDraft from "./components/CampaignDraft";
import OfferForm from "./components/OfferForm";
import type { CampaignDraftData, CampaignDraftInput, OperationPreview } from "./types";

const initialInput: CampaignDraftInput = {
  offer_name: "",
  benefit: "Aprenda uma habilidade prática",
  audience: "profissionais iniciantes",
  proof: "método em aulas curtas",
  cta: "Comece agora",
  price: "47",
  gross_margin_pct: "80",
  checkout_conversion_pct: "2",
  refund_pct: "10",
  currency: "BRL",
  budget: "36",
  platforms: ["meta", "google"],
};

export default function App() {
  const [input, setInput] = useState(initialInput);
  const [draft, setDraft] = useState<CampaignDraftData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [preview, setPreview] = useState<OperationPreview | null>(null);
  const [approvalBusy, setApprovalBusy] = useState(false);
  const [applied, setApplied] = useState(false);

  const createDraft = async () => {
    setLoading(true);
    setError("");
    try {
      setDraft(await generateDraft(input));
      setPreview(null);
      setApplied(false);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível gerar o rascunho.");
    } finally {
      setLoading(false);
    }
  };

  const preparePreview = async () => {
    setLoading(true);
    setError("");
    try {
      setPreview(await previewOperation("meta", input.budget, input));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível preparar a prévia.");
    } finally {
      setLoading(false);
    }
  };

  const approve = async () => {
    if (!preview) return;
    setApprovalBusy(true);
    setError("");
    try {
      await approveOperation(preview.operation_id, preview.token);
      setApplied(true);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Não foi possível aplicar a operação.");
    } finally {
      setApprovalBusy(false);
    }
  };

  return (
    <main className="shell">
      <header className="hero"><p className="eyebrow">LOW-TICKET ADS STUDIO</p><h1>Campanhas com controle antes do gasto.</h1><p className="intro">Planeje, valide e analise anúncios de Meta e Google localmente.</p><div className="status-card" aria-label="Status da aplicação"><span className="status-dot" /><div><strong>Modo seguro ativo</strong><p>Nenhuma alteração é publicada sem prévia e aprovação.</p></div></div></header>
      <OfferForm value={input} onChange={setInput} onSubmit={createDraft} loading={loading} />
      {error && <p className="error" role="alert">{error}</p>}
      {draft && <>
        <CampaignDraft draft={draft} />
        <button className="primary-button standalone-action" type="button" onClick={preparePreview} disabled={loading}>{loading ? "Preparando…" : "Preparar prévia"}</button>
        <ApprovalDialog preview={preview} onApprove={approve} busy={approvalBusy} />
        {applied && <p className="success" role="status">Operação aplicada com campanha pausada.</p>}
      </>}
    </main>
  );
}
