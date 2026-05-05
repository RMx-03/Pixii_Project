import type { DiagnosticResponse } from "@/lib/types";

/**
 * Action plan recommendations panel.
 */
export function ActionPlan({ report }: { report: DiagnosticResponse }) {
  return (
    <section className="card">
      <h3>Action Plan</h3>
      <p className="muted">
        Target recommendation:{" "}
        <strong>{report.target_analysis.is_recommended ? "Recommended" : "Not Recommended"}</strong>
        {report.target_analysis.best_rank ? ` | Best rank: #${report.target_analysis.best_rank}` : ""}
      </p>
      <h5>Priority Tasks</h5>
      <ul>
        {report.action_plan.priority_tasks.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <h5>Title Changes</h5>
      <ul>
        {report.action_plan.title_changes.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <h5>Bullet Changes</h5>
      <ul>
        {report.action_plan.bullet_changes.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
      <h5>FAQ Changes</h5>
      <ul>
        {report.action_plan.faq_changes.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </section>
  );
}

