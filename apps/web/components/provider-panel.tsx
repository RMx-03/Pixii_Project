import type { NormalizedProviderOutput } from "@/lib/shared-types";

/**
 * Provider comparison panel.
 */
export function ProviderPanel({ provider }: { provider: NormalizedProviderOutput }) {
  return (
    <article className="card">
      <div className="provider-header">
        <h4>{provider.provider_name.toUpperCase()}</h4>
        <span className="pill">{provider.overall_verdict.replace("_", " ")}</span>
      </div>
      <p className="muted">Model: {provider.model}</p>
      <p>{provider.raw_answer_excerpt}</p>
      <h5>Evidence</h5>
      <ul>
        {provider.evidence_snippets.map((snippet) => (
          <li key={snippet}>{snippet}</li>
        ))}
      </ul>
      <h5>Recommended Products</h5>
      <ul>
        {provider.recommended_products.length ? (
          provider.recommended_products.map((item) => (
            <li key={`${item.name}-${item.rank_hint ?? "x"}`}>
              #{item.rank_hint ?? "-"} {item.name}
            </li>
          ))
        ) : (
          <li>None surfaced.</li>
        )}
      </ul>
    </article>
  );
}
