const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000').replace(/\/+$/, '');

export interface ApiHealth {
  status?: string;
  service?: string;
  [key: string]: unknown;
}

export interface DashboardSummary {
  influencers_indexed: number;
  campaigns_analyzed: number;
  data_source: string;
}

export function getApiBaseUrl(): string {
  return API_BASE_URL;
}

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        Accept: 'application/json',
        ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
        ...init?.headers,
      },
    });
  } catch {
    throw new Error(`Cannot connect to ${API_BASE_URL}. Check that FastAPI is running and CORS allows the frontend origin.`);
  }

  const contentType = response.headers.get('content-type') || '';
  const body = contentType.includes('application/json')
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail =
      typeof body === 'object' && body !== null && 'detail' in body
        ? String((body as { detail: unknown }).detail)
        : typeof body === 'string' && body
          ? body
          : response.statusText;
    throw new Error(`API request failed (${response.status}): ${detail}`);
  }

  return body as T;
}

export function getHealth(): Promise<ApiHealth> {
  return requestJson<ApiHealth>('/health');
}

export function getDashboardSummary(): Promise<DashboardSummary> {
  return requestJson<DashboardSummary>('/api/dashboard/summary');
}

/**
 * Calls the existing LLM campaign interpretation endpoint.
 * Confirm that CampaignBriefRequest uses the "brief" field.
 */
export function interpretCampaign(brief: string): Promise<unknown> {
  return requestJson<unknown>('/api/llm/interpret-campaign', {
    method: 'POST',
    body: JSON.stringify({ brief }),
  });
}


export interface BrandOption {
  brand_id: string;
  brand_name: string;
  primary_category: string;
}

export interface MatchResult {
  influencer_id: string;
  display_name?: string;
  verified?: boolean;
  match_score: number;
  audience_fit: number;
  engagement_quality: number;
  brand_affinity: number;
  historical_performance: number;
  cost_effectiveness: number;
  estimated_cost: number;
  follower_count: number;
  platform: string;
  primary_niche: string;
  location: string;
  score_breakdown: Record<string, number | null>;
}

export interface MatchResponse {
  brand_id: string;
  count: number;
  results: MatchResult[];
  ranking_method: string;
  weights?: Record<string, number>;
  note?: string;
}

export interface EvaluationModel {
  model: string;
  precision_at_10: number;
  recall_at_10: number;
  ndcg_at_10: number;
}

export interface EvaluationSummary {
  status: string;
  source?: string;
  k?: number;
  models?: EvaluationModel[];
  evaluation_cases?: number | null;
  note?: string;
}

export function getBrands(): Promise<{ brands: BrandOption[] }> {
  return requestJson<{ brands: BrandOption[] }>('/api/matching/brands');
}

export function getRecommendations(
  brandId: string,
  criteria: Record<string, unknown>,
  topK = 10,
): Promise<MatchResponse> {
  return requestJson<MatchResponse>('/api/matching/recommendations', {
    method: 'POST',
    body: JSON.stringify({ brand_id: brandId, criteria, top_k: topK }),
  });
}

export function explainRecommendation(
  campaign: Record<string, unknown>,
  influencerId: string,
  scores: Record<string, number>,
): Promise<unknown> {
  return requestJson<unknown>('/api/matching/explain', {
    method: 'POST',
    body: JSON.stringify({ campaign, influencer_id: influencerId, scores }),
  });
}

export function getEvaluationSummary(): Promise<EvaluationSummary> {
  return requestJson<EvaluationSummary>('/api/evaluation/summary');
}
