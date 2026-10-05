import type { CampaignDraftData, Platform } from "../types";

export default function CampaignDraft({ draft }: { draft: CampaignDraftData }) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <p className="eyebrow">02 / CRIATIVOS</p>
          <h2>Rascunho pausado</h2>
        </div>
        <span className="pill safe">{draft.status}</span>
      </div>
      <p className="muted">Orçamento sugerido: {draft.budget}. Nenhuma campanha foi publicada.</p>
      <div className="variant-grid">
        {(Object.entries(draft.variants) as [Platform, NonNullable<typeof draft.variants[Platform]>][]).flatMap(([platform, variants]) =>
          (variants ?? []).map((variant) => (
            <article className="variant-card" key={`${platform}-${variant.angle}`}>
              <div className="variant-topline"><span className="platform-badge">{platform}</span><span>{variant.angle}</span></div>
              <strong>{variant.copy.headline ?? variant.copy.google_headlines?.[0]}</strong>
              <p>{variant.copy.primary_text ?? variant.copy.google_descriptions?.[0]}</p>
              <small>{variant.creative_brief}</small>
              {variant.validation_issues.map((issue) => <div className="issue" key={`${issue.field}-${issue.actual}`}>{issue.message}</div>)}
            </article>
          )),
        )}
      </div>
    </section>
  );
}
