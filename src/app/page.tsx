import { io } from "next/cache";
import { Suspense } from "react";

import { AutomationDashboard } from "@/components/automation-dashboard";
import { buildSampleProfiles } from "@/config/sample-profiles";

export default function Home() {
  return (
    <Suspense
      fallback={
        <main className="mx-auto flex w-full max-w-7xl flex-1 items-center justify-center px-4 py-12 text-sm text-slate-500">
          Preparing sample clinician schedules…
        </main>
      }
    >
      <RequestTimeDashboard />
    </Suspense>
  );
}

async function RequestTimeDashboard() {
  await io();
  const formUrl =
    process.env.NEXT_PUBLIC_GOOGLE_FORM_URL ?? "https://forms.gle/4Qn7MCvAzMBrR1Hw7";

  return <AutomationDashboard defaultFormUrl={formUrl} profiles={buildSampleProfiles()} />;
}
