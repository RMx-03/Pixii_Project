import Link from "next/link";
import { ActionPlan } from "@/components/action-plan";
import { ProviderPanel } from "@/components/provider-panel";
import { RerunForm } from "@/components/rerun-form";
import { Scorecard } from "@/components/scorecard";
import { Warnings } from "@/components/warnings";
import { getExportUrl, getRun } from "@/lib/api";

/**
 * Report details page.
 */
export default async function ReportPage({ params }: { params: Promise<{ runId: string }> }) {
  const resolved = await params;
  const report = await getRun(resolved.runId);
  return (
    <main className="shell">
      <header className="hero compact">
        <div>
          <p className="kicker">AEO Report</p>
          <h1>Run {report.run_id}</h1>
          <p className="muted">
            Mode: <strong>{report.mode}</strong> | Providers: {report.providers.length}
          </p>
        </div>
        <div className="header-actions">
          <a href={getExportUrl(report.run_id, "md")} className="ghost-button">
            Export Markdown
          </a>
          <a href={getExportUrl(report.run_id, "pdf")} className="ghost-button">
            Export PDF
          </a>
          <Link className="ghost-button" href="/">
            New Run
          </Link>
        </div>
      </header>

      <Warnings warnings={report.warnings} />
      <Scorecard score={report.scorecard} />
      <ActionPlan report={report} />
      <RerunForm report={report} />

      <section className="provider-grid">
        {report.providers.map((provider) => (
          <ProviderPanel key={provider.provider_name} provider={provider} />
        ))}
      </section>
    </main>
  );
}
