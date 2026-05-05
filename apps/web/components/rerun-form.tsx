"use client";

import { useState } from "react";
import { rerunDiagnostic } from "@/lib/api";
import type { DiagnosticResponse, RerunResponse } from "@/lib/types";

/**
 * Rerun trigger and delta display.
 */
export function RerunForm({ report }: { report: DiagnosticResponse }) {
  const [query, setQuery] = useState(report.query);
  const [targetUrl, setTargetUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [delta, setDelta] = useState<RerunResponse["delta"] | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function handleRerun() {
    setLoading(true);
    setError(null);
    try {
      const rerun = await rerunDiagnostic({
        baselineRunId: report.run_id,
        targetUrl: targetUrl || report.target_url,
        query,
        competitorMode: "auto",
        competitorUrls: [],
      });
      setDelta(rerun.delta);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unknown error";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h3>Re-run After Listing Edits</h3>
      <div className="form-grid">
        <label>
          Updated Target URL
          <input
            value={targetUrl}
            onChange={(event) => setTargetUrl(event.target.value)}
            placeholder="Leave empty to reuse baseline context"
          />
        </label>
        <label>
          Query
          <input value={query} onChange={(event) => setQuery(event.target.value)} />
        </label>
      </div>
      <div className="actions">
        <button type="button" onClick={handleRerun} disabled={loading}>
          {loading ? "Running..." : "Run Comparison"}
        </button>
      </div>
      {delta ? (
        <div className="delta-grid">
          <DeltaTile label="Overall" value={delta.overall_delta} />
          <DeltaTile label="Visibility" value={delta.visibility_delta} />
          <DeltaTile label="Relevance" value={delta.relevance_delta} />
          <DeltaTile label="Sentiment" value={delta.sentiment_delta} />
          <DeltaTile label="Trust" value={delta.trust_delta} />
        </div>
      ) : null}
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}

/**
 * Rerun delta display tile.
 */
function DeltaTile({ label, value }: { label: string; value: number }) {
  const sign = value > 0 ? "+" : "";
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{`${sign}${value}`}</strong>
    </div>
  );
}
