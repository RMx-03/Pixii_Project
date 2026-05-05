import type { Scorecard as ScorecardType } from "@/lib/shared-types";

/**
 * Scorecard panel.
 */
export function Scorecard({ score }: { score: ScorecardType }) {
  return (
    <section className="card">
      <h3>Scorecard</h3>
      <div className="score-grid">
        <ScoreMetric label="Overall" value={score.overall} />
        <ScoreMetric label="Visibility" value={score.visibility} />
        <ScoreMetric label="Relevance" value={score.relevance} />
        <ScoreMetric label="Sentiment" value={score.sentiment} />
        <ScoreMetric label="Trust" value={score.trust} />
      </div>
    </section>
  );
}

/**
 * Single score metric.
 */
function ScoreMetric({ label, value }: { label: string; value: number }) {
  return (
    <div className="metric">
      <div className="metric-header">
        <span>{label}</span>
        <strong>{value}</strong>
      </div>
      <div className="bar-track">
        <div className="bar-fill" style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}
