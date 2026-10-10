export type EmployeeStatus = "pending" | "filling" | "ready" | "submitted" | "failed";
export type RunStatus = "pending" | "running" | "ready" | "completed" | "failed";

export type ClinicianResult = {
  id: string;
  email: string;
  clinician_name: string;
  student_number: string;
  scheduled_day: string;
  shift_schedule: string;
  department: string;
  time_interval: string;
  status: EmployeeStatus;
  error: string | null;
};

export type RunSummary = Record<EmployeeStatus, number> & { total: number };

export type TestRun = {
  id: string;
  status: RunStatus;
  submit: boolean;
  created_at: string;
  started_at: string | null;
  finished_at: string | null;
  execution_ms: number | null;
  error: string | null;
  summary: RunSummary;
  results: ClinicianResult[];
};

type CreatedRun = { job_id: string; status: RunStatus; prefill_urls: string[] };

const API_BASE_URL = (
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000"
).replace(/\/$/, "");

export function usesRemoteAutomationApi() {
  try {
    const hostname = new URL(API_BASE_URL).hostname;
    return hostname !== "localhost" && hostname !== "127.0.0.1" && hostname !== "::1";
  } catch {
    return false;
  }
}

async function parseResponse<T>(response: Response): Promise<T> {
  if (response.ok) return response.json() as Promise<T>;

  let message = "The automation service returned an unexpected error.";
  try {
    const payload = (await response.json()) as { detail?: string };
    if (payload.detail) message = payload.detail;
  } catch {
    // Keep the safe fallback for non-JSON failures.
  }
  throw new Error(message);
}

export async function createTestRun(
  formUrl: string,
  submit: boolean,
  signal?: AbortSignal,
) {
  const response = await fetch(`${API_BASE_URL}/test-runs`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ form_url: formUrl, submit }),
    signal,
  });
  return parseResponse<CreatedRun>(response);
}

export async function getTestRun(jobId: string, signal?: AbortSignal) {
  const response = await fetch(`${API_BASE_URL}/test-runs/${jobId}`, {
    cache: "no-store",
    signal,
  });
  return parseResponse<TestRun>(response);
}
