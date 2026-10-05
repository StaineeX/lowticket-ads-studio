import { FormEvent } from "react";
import type { CampaignDraftInput, Platform } from "../types";

type Props = {
  value: CampaignDraftInput;
  onChange: (next: CampaignDraftInput) => void;
  onSubmit: () => void;
  loading: boolean;
};

export default function OfferForm({ value, onChange, onSubmit, loading }: Props) {
  const update = (field: keyof CampaignDraftInput, next: string) =>
    onChange({ ...value, [field]: next });
  const submit = (event: FormEvent) => {
    event.preventDefault();
    onSubmit();
  };

  return (
    <form className="panel form-grid" onSubmit={submit}>
      <div className="panel-heading">
        <div>
          <p className="eyebrow">01 / OFERTA</p>
          <h2>Defina a economia antes do anúncio</h2>
        </div>
        <span className="pill">rascunho local</span>
      </div>
      <label>Nome da oferta<input value={value.offer_name} onChange={(e) => update("offer_name", e.target.value)} required /></label>
      <label>Benefício principal<input value={value.benefit} onChange={(e) => update("benefit", e.target.value)} required /></label>
      <label>Público<input value={value.audience} onChange={(e) => update("audience", e.target.value)} required /></label>
      <label>Prova/mecanismo<input value={value.proof} onChange={(e) => update("proof", e.target.value)} required /></label>
      <label>CTA<input value={value.cta} onChange={(e) => update("cta", e.target.value)} required /></label>
      <label>Preço<input aria-label="Preço" type="number" step="0.01" value={value.price} onChange={(e) => update("price", e.target.value)} required /></label>
      <label>Margem bruta (%)<input aria-label="Margem bruta (%)" type="number" value={value.gross_margin_pct} onChange={(e) => update("gross_margin_pct", e.target.value)} required /></label>
      <label>Conversão do checkout (%)<input aria-label="Conversão do checkout (%)" type="number" value={value.checkout_conversion_pct} onChange={(e) => update("checkout_conversion_pct", e.target.value)} required /></label>
      <label>Orçamento diário<input type="number" step="0.01" value={value.budget} onChange={(e) => update("budget", e.target.value)} required /></label>
      <div className="platforms" aria-label="Plataformas">
        <span>Meta + Google</span>
        <span className="platform-badge">{value.platforms.join(" / ")}</span>
      </div>
      <button className="primary-button" type="submit" disabled={loading}>{loading ? "Gerando…" : "Gerar rascunho"}</button>
    </form>
  );
}
