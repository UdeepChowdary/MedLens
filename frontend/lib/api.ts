/**
 * MedLens API Client
 * Typed, centralized HTTP client for all backend API calls.
 * Falls back gracefully when backend is unavailable (dev mode).
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

// ─── Types ────────────────────────────────────────────────────────────────────

export type VerificationState =
  | "verified"
  | "partially_verified"
  | "needs_confirmation"
  | "unable_to_verify";

export type ComparisonOutcome = "match" | "difference" | "unknown" | "conflict" | "not_applicable";

export interface EvidenceSource {
  name: string;
  url: string;
  source_id?: string;
  jurisdiction?: string;
  retrieval_date?: string;
}

export interface Strength {
  raw_text: string;
  numeric_value?: number;
  unit: string;
  basis?: string;
}

export interface IngredientReport {
  canonical_name: string;
  raw_label_text: string;
  strength: Strength;
  role: "active" | "inactive" | "unknown";
  confidence: number;
  explanation: string;
  therapeutic_purpose: string;
  evidence_sources: EvidenceSource[];
}

export interface SafetyProfile {
  purpose_summary: string;
  precautions: string[];
  contraindications: string[];
  adverse_effects: string[];
}

export interface ProductReport {
  id?: string;
  detected_name: string;
  dosage_form: string;
  manufacturer?: string;
  is_verified: boolean;
}

export interface MultidimensionalConfidence {
  ocr_quality: number;
  extraction_quality: number;
  identity_confidence: number;
  evidence_coverage: number;
}

export interface AnalysisCreateResponse {
  analysis_id: string;
  status: string;
  created_at: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  status: VerificationState;
  processing_time_ms: number;
  confidence: MultidimensionalConfidence;
  product: ProductReport;
  active_ingredients: IngredientReport[];
  inactive_ingredients: IngredientReport[];
  safety_profile: SafetyProfile;
  uncertainties: string[];
  audit_hash: string;
  sources: EvidenceSource[];
  limitations: string[];
}

export interface AttributeComparison {
  field: string;
  result: ComparisonOutcome;
  evidence: string[];
  reason?: string;
}

export interface StrengthDelta {
  difference_detected: boolean;
  numeric_delta?: number;
  unit?: string;
  warning?: string;
}

export interface ComparisonResponse {
  comparison_status: string;
  medicine_a: { product_id: string; name: string; manufacturer?: string };
  medicine_b: { product_id: string; name: string; manufacturer?: string };
  attributes: AttributeComparison[];
  strength_delta?: StrengthDelta;
  excipient_differences: string[];
  therapeutic_equivalence: { status: string; note: string };
  limitations: string[];
  sources: string[];
}

export interface InteractionRecord {
  ingredient_a: string;
  ingredient_b: string;
  severity: string;
  clinical_effect: string;
  source_id: string;
  coverage_note: string;
}

export type ApiError = {
  error_code: string;
  message: string;
  details?: Record<string, unknown>;
};

// ─── HTTP Helper ──────────────────────────────────────────────────────────────

async function request<T>(
  path: string,
  options?: RequestInit
): Promise<{ data: T | null; error: ApiError | null }> {
  try {
    const res = await fetch(`${API_BASE}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(options?.headers ?? {}),
      },
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error_code: "ERR_UNKNOWN", message: res.statusText }));
      return { data: null, error: err as ApiError };
    }

    const data = await res.json();
    return { data: data as T, error: null };
  } catch {
    return {
      data: null,
      error: {
        error_code: "ERR_NETWORK",
        message: "Could not reach the MedLens backend. Ensure the server is running on port 8000.",
      },
    };
  }
}

// ─── API Functions ────────────────────────────────────────────────────────────

/** Upload a medicine packaging image and receive a tracking ID. */
export async function uploadAnalysis(
  file: File
): Promise<{ data: AnalysisCreateResponse | null; error: ApiError | null }> {
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch(`${API_BASE}/analyses`, {
      method: "POST",
      body: formData,
      // Do NOT set Content-Type header for multipart; browser sets it with boundary
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ error_code: "ERR_UPLOAD", message: res.statusText }));
      return { data: null, error: err as ApiError };
    }

    const data = await res.json();
    return { data: data as AnalysisCreateResponse, error: null };
  } catch {
    return {
      data: null,
      error: { error_code: "ERR_NETWORK", message: "Upload failed. Ensure the backend is running." },
    };
  }
}

/** Retrieve a completed analysis report by ID. */
export async function getAnalysis(
  analysisId: string
): Promise<{ data: AnalysisResponse | null; error: ApiError | null }> {
  return request<AnalysisResponse>(`/analyses/${analysisId}`);
}

/** Poll analysis status (for real-time pipeline progress). */
export async function pollAnalysis(
  analysisId: string,
  onProgress: (status: string) => void,
  maxAttempts = 30
): Promise<AnalysisResponse | null> {
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise((r) => setTimeout(r, 1000)); // 1 second interval
    const { data, error } = await getAnalysis(analysisId);

    if (error) {
      onProgress("error");
      return null;
    }

    if (data) {
      const s = data.status;
      onProgress(s);
      if (
        s === "verified" ||
        s === "partially_verified" ||
        s === "needs_confirmation" ||
        s === "unable_to_verify"
      ) {
        return data;
      }
    }
  }
  return null;
}

/** Search the product catalog. */
export async function searchProducts(
  query: string
): Promise<{ data: ProductReport[] | null; error: ApiError | null }> {
  return request<ProductReport[]>(`/products/search?q=${encodeURIComponent(query)}`);
}

/** Get a product by ID. */
export async function getProduct(
  productId: string
): Promise<{ data: ProductReport | null; error: ApiError | null }> {
  return request<ProductReport>(`/products/${productId}`);
}

/** Compare two products deterministically. */
export async function compareProducts(
  productIdA: string,
  productIdB: string
): Promise<{ data: ComparisonResponse | null; error: ApiError | null }> {
  return request<ComparisonResponse>(`/comparisons`, {
    method: "POST",
    body: JSON.stringify({ product_id_a: productIdA, product_id_b: productIdB }),
  });
}

/** Check interactions between ingredients. */
export async function checkInteractions(
  ingredientIds: string[]
): Promise<{ data: InteractionRecord[] | null; error: ApiError | null }> {
  return request<InteractionRecord[]>(`/interactions/check`, {
    method: "POST",
    body: JSON.stringify({ ingredient_ids: ingredientIds }),
  });
}

/** Health check. */
export async function checkHealth(): Promise<boolean> {
  const { data } = await request<{ status: string }>(`/health`);
  return data?.status === "ok";
}
