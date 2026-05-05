import { z } from "zod";
import type { DiagnosticResponse, RerunResponse } from "./types";

const runSchema = z.object({
  targetUrl: z.string().url(),
  query: z.string().min(3),
  competitorMode: z.enum(["manual", "auto"]),
  competitorUrls: z.array(z.string().url()).max(5),
  baselineRunId: z.string().optional(),
});

const rerunSchema = z.object({
  baselineRunId: z.string().min(1),
  targetUrl: z.string().url(),
  query: z.string().min(3),
  competitorMode: z.enum(["manual", "auto"]),
  competitorUrls: z.array(z.string().url()).max(5),
});

const API_BASE = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

/**
 * Run a new diagnostic.
 */
export async function runDiagnostic(input: z.infer<typeof runSchema>): Promise<DiagnosticResponse> {
  const payload = runSchema.parse(input);
  const response = await fetch(`${API_BASE}/api/v1/diagnostics/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      target_url: payload.targetUrl,
      query: payload.query,
      competitor_mode: payload.competitorMode,
      competitor_urls: payload.competitorUrls,
      baseline_run_id: payload.baselineRunId ?? null,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to run diagnostic: ${response.status}`);
  }
  return (await response.json()) as DiagnosticResponse;
}

/**
 * Run a rerun against baseline.
 */
export async function rerunDiagnostic(input: z.infer<typeof rerunSchema>): Promise<RerunResponse> {
  const payload = rerunSchema.parse(input);
  const response = await fetch(`${API_BASE}/api/v1/diagnostics/rerun`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      baseline_run_id: payload.baselineRunId,
      target_url: payload.targetUrl,
      query: payload.query,
      competitor_mode: payload.competitorMode,
      competitor_urls: payload.competitorUrls,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to rerun diagnostic: ${response.status}`);
  }
  return (await response.json()) as RerunResponse;
}

/**
 * Load report by id.
 */
export async function getRun(runId: string): Promise<DiagnosticResponse> {
  const response = await fetch(`${API_BASE}/api/v1/diagnostics/runs/${runId}`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error(`Failed to load report: ${response.status}`);
  }
  return (await response.json()) as DiagnosticResponse;
}

/**
 * Get export URL.
 */
export function getExportUrl(runId: string, format: "md" | "pdf"): string {
  return `${API_BASE}/api/v1/diagnostics/reports/${runId}/export?format=${format}`;
}

