type Recommendation = { type: string; rationale: string; risk_level: string };

export default function RecommendationList({ items }: { items: Recommendation[] }) {
  if (!items.length) return <p className="muted">Ainda não há recomendações.</p>;
  return <div className="recommendations">{items.map((item, index) => <article className="recommendation" key={`${item.type}-${index}`}><span className="platform-badge">{item.type}</span><p>{item.rationale}</p><small>risco {item.risk_level}</small></article>)}</div>;
}
