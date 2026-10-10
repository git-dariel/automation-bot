"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import type { SampleProfile } from "@/config/sample-profiles";
import {
  createTestRun,
  getTestRun,
  type EmployeeStatus,
  type TestRun,
  usesRemoteAutomationApi,
} from "@/lib/test-runs";

const statusStyles: Record<EmployeeStatus, string> = {
  pending: "bg-slate-100 text-slate-600",
  filling: "bg-amber-100 text-amber-800",
  ready: "bg-blue-100 text-blue-800",
  submitted: "bg-emerald-100 text-emerald-800",
  failed: "bg-red-100 text-red-800",
};

function formatDuration(value: number | null) {
  if (value === null) return "—";
  return value < 1000 ? `${value} ms` : `${(value / 1000).toFixed(1)} s`;
}

function delay(milliseconds: number, signal: AbortSignal) {
  return new Promise<void>((resolve, reject) => {
    const timer = window.setTimeout(resolve, milliseconds);
    signal.addEventListener(
      "abort",
      () => {
        window.clearTimeout(timer);
        reject(new DOMException("Aborted", "AbortError"));
      },
      { once: true },
    );
  });
}

type AutomationDashboardProps = {
  defaultFormUrl: string;
  profiles: SampleProfile[];
};

export function AutomationDashboard({ defaultFormUrl, profiles }: AutomationDashboardProps) {
  const opensClientTabs = usesRemoteAutomationApi();
  const [formUrl, setFormUrl] = useState(defaultFormUrl);
  const [submit, setSubmit] = useState(false);
  const [run, setRun] = useState<TestRun | null>(null);
  const [isStarting, setIsStarting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const requestRef = useRef<AbortController | null>(null);

  const isActive =
    isStarting || run?.status === "pending" || run?.status === "running" || run?.status === "ready";

  const visibleProfiles = useMemo(() => {
    return profiles.map((profile) => {
      const result = run?.results.find((item) => item.id === profile.id);
      return {
        ...profile,
        status: result?.status ?? "pending",
        error: result?.error ?? null,
      } satisfies SampleProfile & { status: EmployeeStatus; error: string | null };
    });
  }, [profiles, run]);

  useEffect(() => () => requestRef.current?.abort(), []);

  async function pollRun(jobId: string, signal: AbortSignal) {
    while (!signal.aborted) {
      const nextRun = await getTestRun(jobId, signal);
      setRun(nextRun);
      if (nextRun.status === "completed" || nextRun.status === "failed") return;
      await delay(1000, signal);
    }
  }

  async function handleStart() {
    if (submit) {
      const confirmed = window.confirm(
        `This will submit ${profiles.length} test responses to the Google Form. Continue?`,
      );
      if (!confirmed) return;
    }

    const clientTabs = opensClientTabs
      ? profiles.map(() => window.open("about:blank", "_blank"))
      : [];
    let tabsWereNavigated = false;
    if (clientTabs.some((tab) => tab === null)) {
      clientTabs.forEach((tab) => tab?.close());
      setError(
        `Chrome blocked one or more tabs. Allow pop-ups for this site, then start the test again.`,
      );
      return;
    }

    clientTabs.forEach((tab, index) => {
      if (!tab) return;
      tab.document.title = `Preparing clinician ${index + 1}`;
      tab.document.body.textContent = "Preparing the prefilled Google Form…";
    });

    requestRef.current?.abort();
    const controller = new AbortController();
    requestRef.current = controller;
    setError(null);
    setRun(null);
    setIsStarting(true);

    try {
      const created = await createTestRun(formUrl.trim(), submit, controller.signal);
      if (opensClientTabs) {
        if (created.prefill_urls.length !== clientTabs.length) {
          throw new Error("The API did not return all visible form tabs.");
        }
        clientTabs.forEach((tab, index) => {
          if (!tab) return;
          tab.location.replace(created.prefill_urls[index]);
          tab.opener = null;
        });
        tabsWereNavigated = true;
      }
      await pollRun(created.job_id, controller.signal);
    } catch (caught) {
      if (!tabsWereNavigated) clientTabs.forEach((tab) => tab?.close());
      if (caught instanceof DOMException && caught.name === "AbortError") return;
      setError(caught instanceof Error ? caught.message : "Unable to start the test run.");
    } finally {
      if (!controller.signal.aborted) setIsStarting(false);
    }
  }

  return (
    <main className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-8 bg-slate-50 px-4 py-8 sm:px-6 lg:px-8 lg:py-12">
      <section className="flex flex-col gap-3 border-b border-slate-200 pb-7 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="mb-2 text-sm font-semibold uppercase tracking-[0.16em] text-blue-700">
            Browser automation prototype
          </p>
          <h1 className="text-3xl font-semibold tracking-tight text-slate-950 sm:text-4xl">
            Clinic sign-up test runner
          </h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-600 sm:text-base">
            Fill {profiles.length} visible Chromium tabs with isolated, fabricated clinician data.
            Submission stays off unless you deliberately enable it.
          </p>
        </div>
        <div className="mt-2 flex items-center gap-2 text-sm text-slate-600 sm:mt-0">
          <span className="size-2 rounded-full bg-emerald-500" aria-hidden="true" />
          {opensClientTabs ? "Cloud API + visible tabs" : "Local browser mode"}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_320px]">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="flex flex-col gap-5">
            <div>
              <label htmlFor="form-url" className="text-sm font-medium text-slate-900">
                Google Form URL
              </label>
              <p id="form-url-help" className="mt-1 text-sm text-slate-500">
                Paste any public forms.gle or docs.google.com/forms link.
              </p>
              <input
                id="form-url"
                type="url"
                value={formUrl}
                onChange={(event) => setFormUrl(event.target.value)}
                aria-describedby="form-url-help"
                disabled={isActive}
                className="mt-3 h-11 w-full rounded-lg border border-slate-300 bg-white px-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-600 focus:ring-4 focus:ring-blue-100 disabled:cursor-not-allowed disabled:bg-slate-100"
                required
              />
            </div>

            <div className="flex flex-col gap-4 border-t border-slate-200 pt-5 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-start gap-3">
                <button
                  type="button"
                  role="switch"
                  aria-checked={submit}
                  disabled={isActive}
                  onClick={() => setSubmit((value) => !value)}
                  className={`relative mt-0.5 h-6 w-11 shrink-0 rounded-full transition focus:outline-none focus:ring-4 focus:ring-blue-100 disabled:cursor-not-allowed disabled:opacity-60 ${
                    submit ? "bg-blue-600" : "bg-slate-300"
                  }`}
                >
                  <span
                    className={`absolute left-1 top-1 size-4 rounded-full bg-white shadow-sm transition-transform ${
                      submit ? "translate-x-5" : "translate-x-0"
                    }`}
                    aria-hidden="true"
                  />
                  <span className="sr-only">Test Submit</span>
                </button>
                <div>
                  <p className="text-sm font-medium text-slate-900">Test Submit</p>
                  <p className="text-sm text-slate-500">
                    {submit
                      ? `${profiles.length} responses will be submitted after verification.`
                      : "Fill and verify only."}
                  </p>
                </div>
              </div>

              <button
                type="button"
                onClick={handleStart}
                disabled={isActive || !formUrl.trim()}
                className="inline-flex h-11 min-w-36 items-center justify-center rounded-lg bg-blue-700 px-5 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-800 focus:outline-none focus:ring-4 focus:ring-blue-200 disabled:cursor-not-allowed disabled:bg-slate-300"
              >
                {isStarting ? "Starting…" : submit ? "Start & submit" : "Start test"}
              </button>
            </div>
          </div>
        </div>

        <aside className="rounded-2xl border border-slate-200 bg-slate-950 p-5 text-white shadow-sm sm:p-6">
          <p className="text-sm font-medium text-slate-300">Run summary</p>
          <p className="mt-1 text-xl font-semibold capitalize">{run?.status ?? "Not started"}</p>
          <dl className="mt-6 grid grid-cols-2 gap-x-4 gap-y-5 text-sm">
            <div><dt className="text-slate-400">Ready</dt><dd className="mt-1 text-2xl font-semibold">{run?.summary.ready ?? 0}</dd></div>
            <div><dt className="text-slate-400">Submitted</dt><dd className="mt-1 text-2xl font-semibold">{run?.summary.submitted ?? 0}</dd></div>
            <div><dt className="text-slate-400">Failed</dt><dd className="mt-1 text-2xl font-semibold">{run?.summary.failed ?? 0}</dd></div>
            <div><dt className="text-slate-400">Execution</dt><dd className="mt-2 font-medium">{formatDuration(run?.execution_ms ?? null)}</dd></div>
          </dl>
          {run?.status === "ready" && (
            <p className="mt-6 rounded-lg bg-blue-400/10 p-3 text-sm leading-5 text-blue-100">
              {opensClientTabs
                ? "The prefilled Google Form tabs are ready for inspection."
                : "Tabs are ready for inspection. Close Chromium when finished."}
            </p>
          )}
          {opensClientTabs && run?.status === "completed" && (
            <p className="mt-6 rounded-lg bg-emerald-400/10 p-3 text-sm leading-5 text-emerald-100">
              The prefilled Google Form tabs remain open in your browser.
            </p>
          )}
        </aside>
      </section>

      {error && (
        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
          {error}
        </div>
      )}

      <section aria-labelledby="profiles-title">
        <div className="mb-4 flex items-end justify-between gap-4">
          <div>
            <h2 id="profiles-title" className="text-xl font-semibold text-slate-950">Sample clinicians</h2>
            <p className="mt-1 text-sm text-slate-500">
              {profiles.length} fabricated profiles; no real student data.
            </p>
          </div>
          <span className="text-sm font-medium text-slate-500">{profiles.length} profiles</span>
        </div>

        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {visibleProfiles.map((profile, index) => {
            const status = profile.status;
            const profileError = profile.error;
            return (
              <article key={profile.id} className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">
                <div className="flex items-start justify-between gap-3">
                  <span className="text-xs font-semibold text-slate-400">#{index + 1}</span>
                  <span className={`rounded-full px-2.5 py-1 text-xs font-semibold capitalize ${statusStyles[status]}`}>
                    {status}
                  </span>
                </div>
                <h3 className="mt-4 font-semibold text-slate-950">{profile.clinicianName}</h3>
                <p className="mt-1 font-mono text-xs text-slate-500">{profile.studentNumber}</p>
                <p className="mt-1 break-all text-xs text-slate-500">{profile.email}</p>
                <dl className="mt-5 space-y-3 text-sm">
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Schedule</dt>
                    <dd className="mt-1 leading-5 text-slate-700">
                      {profile.scheduledDay} · {profile.shiftSchedule}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Procedure</dt>
                    <dd className="mt-1 leading-5 text-slate-700">{profile.department}</dd>
                  </div>
                  <div>
                    <dt className="text-xs font-medium uppercase tracking-wide text-slate-400">Time required</dt>
                    <dd className="mt-1 leading-5 text-slate-700">{profile.timeInterval}</dd>
                  </div>
                </dl>
                {profileError && <p className="mt-4 text-xs leading-5 text-red-700">{profileError}</p>}
              </article>
            );
          })}
        </div>
      </section>
    </main>
  );
}
