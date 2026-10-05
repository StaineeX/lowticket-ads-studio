import type { OperationPreview } from "../types";

type Props = { preview: OperationPreview | null; onApprove: () => void; busy?: boolean };

export default function ApprovalDialog({ preview, onApprove, busy = false }: Props) {
  return (
    <section className="panel approval-panel">
      <div className="panel-heading"><div><p className="eyebrow">03 / SEGURANÇA</p><h2>Prévia antes de publicar</h2></div><span className="pill">aprovação manual</span></div>
      {preview ? <><p>{preview.summary}</p><small className="muted">Expira em {new Date(preview.expires_at).toLocaleString("pt-BR")}</small></> : <p className="muted">Gere uma prévia para habilitar a aprovação.</p>}
      <button className="primary-button" type="button" onClick={onApprove} disabled={!preview || busy}>{busy ? "Aplicando…" : "Aprovar alteração"}</button>
    </section>
  );
}
