import type { NormalizedProviderOutput, Scorecard } from "./shared-types";

/**
 * API diagnostic response shape.
 */
export interface DiagnosticResponse {
  run_id: string;
  created_at: string;
  target_url: string;
  query: string;
  mode: "live" | "demo";
  providers: NormalizedProviderOutput[];
  scorecard: Scorecard;
  target_analysis: {
    is_recommended: boolean;
    best_rank: number | null;
    confidence: number;
  };
  action_plan: {
    title_changes: string[];
    bullet_changes: string[];
    faq_changes: string[];
    priority_tasks: string[];
  };
  warnings: string[];
  competitor_urls: string[];
}

/**
 * Rerun response shape.
 */
export interface RerunResponse {
  run: DiagnosticResponse;
  delta: {
    baseline_run_id: string;
    current_run_id: string;
    overall_delta: number;
    visibility_delta: number;
    relevance_delta: number;
    sentiment_delta: number;
    trust_delta: number;
    recommendation_changed: boolean;
  };
}
