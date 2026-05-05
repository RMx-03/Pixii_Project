"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { runDiagnostic } from "@/lib/api";

/**
 * Home page diagnostic input wizard.
 */
export function InputWizard() {
  const router = useRouter();
  const [targetUrl, setTargetUrl] = useState("");
  const [query, setQuery] = useState("");
  const [competitorMode, setCompetitorMode] = useState<"manual" | "auto">("auto");
  const [competitorUrlsRaw, setCompetitorUrlsRaw] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleRun() {
    setLoading(true);
    setError(null);
    try {
      const competitorUrls =
        competitorMode === "manual"
          ? competitorUrlsRaw
              .split("\n")
              .map((item) => item.trim())
              .filter(Boolean)
              .slice(0, 5)
          : [];
      const result = await runDiagnostic({
        targetUrl,
        query,
        competitorMode,
        competitorUrls,
      });
      router.push(`/report/${result.run_id}`);
    } catch (cause) {
      const message = cause instanceof Error ? cause.message : "Unknown error";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="card">
      <h2>AEO Diagnostic Input</h2>
      <p className="muted">Evaluate if answer engines recommend your listing for a target shopper query.</p>
      <div className="form-grid">
        <label>
          Target Amazon URL
          <input
            value={targetUrl}
            onChange={(event) => setTargetUrl(event.target.value)}
            placeholder="https://www.amazon.com/dp/..."
          />
        </label>
        <label>
          Shopper Query
          <input
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder="best magnesium supplement for seniors"
          />
        </label>
        <label>
          Competitor Mode
          <select
            value={competitorMode}
            onChange={(event) => setCompetitorMode(event.target.value as "manual" | "auto")}
          >
            <option value="auto">Auto-detect competitors</option>
            <option value="manual">Manual competitor URLs</option>
          </select>
        </label>
        {competitorMode === "manual" ? (
          <label>
            Competitor URLs (one per line)
            <textarea
              rows={6}
              value={competitorUrlsRaw}
              onChange={(event) => setCompetitorUrlsRaw(event.target.value)}
              placeholder="https://www.amazon.com/dp/..."
            />
          </label>
        ) : null}
      </div>
      <div className="actions">
        <button type="button" onClick={handleRun} disabled={loading}>
          {loading ? "Running Diagnostic..." : "Run AEO Report"}
        </button>
      </div>
      {error ? <p className="error">{error}</p> : null}
    </section>
  );
}

