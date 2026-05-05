/**
 * Shared types used by frontend and backend contracts.
 */
export type CompetitorMode = "manual" | "auto";

/**
 * Provider-level recommendation item.
 */
export interface ProviderRecommendation {
  name: string;
  url: string | null;
  reason: string;
  rank_hint: number | null;
}

/**
 * Provider-level normalized response.
 */
export interface NormalizedProviderOutput {
  provider_name: "openai" | "anthropic" | "gemini";
  model: string;
  answered_query: string;
  overall_verdict: "recommended" | "not_recommended" | "uncertain";
  recommended_products: ProviderRecommendation[];
  sentiment_score: number;
  relevance_score: number;
  trust_score: number;
  evidence_snippets: string[];
  raw_answer_excerpt: string;
  suggested_improvements: {
    title: string;
    bullets: string[];
    faqs: string[];
  };
}

/**
 * Final scorecard.
 */
export interface Scorecard {
  visibility: number;
  relevance: number;
  sentiment: number;
  trust: number;
  overall: number;
}
