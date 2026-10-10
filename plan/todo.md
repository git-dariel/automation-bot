# TODO - Clinic Sign-up Google Forms Automation MVP

## Phase 1 - Setup

- [x] Use the existing Next.js TypeScript and Tailwind CSS app.
- [x] Initialize the FastAPI backend structure.
- [x] Add Playwright Python and Chromium setup instructions.
- [x] Verify the current Google Form and its clinic sign-up fields.
- [x] Prepare ten fabricated clinician profiles.

## Phase 2 - Frontend

- [x] Add an editable Google Form URL input.
- [x] Display ten sample clinician profiles.
- [x] Add the Start Test action and duplicate-run prevention.
- [x] Add the Test Submit switch, off by default, with confirmation.
- [x] Display run summary, execution time, and per-profile statuses.
- [x] Handle API validation, conflict, and network errors.
- [x] Use an explicit light theme with accessible contrast.

## Phase 3 - Backend

- [x] Implement `POST /test-runs`.
- [x] Implement `GET /test-runs/{job_id}`.
- [x] Add in-memory job state and thread-safe progress tracking.
- [x] Accept any well-formed public Google Forms URL without an exact form-ID allowlist.
- [x] Reject simultaneous active browser runs.
- [x] Configure local frontend CORS without wildcard origins.

## Phase 4 - Automation

- [x] Launch headed Chromium locally.
- [x] Open ten tabs for the selected test form.
- [x] Assign one fabricated clinician profile per tab.
- [x] Fill and verify email, text, and radio fields by visible label.
- [x] Implement optional form submission.
- [x] Detect the Google Forms confirmation page and capture safe errors.
- [x] Keep fill-only and submitted confirmation tabs open until Chromium is closed manually.

## Phase 5 - Validation

- [x] Run frontend lint, type-check, and production build after the clinic form migration.
- [x] Run the backend automated test suite after the clinic form migration.
- [x] Run a live fill-only test with ten visible tabs.
- [x] Confirm ten-tab concurrency and profile data isolation live.
- [ ] Run an intentional submission test with ten responses.
- [ ] Verify ten distinct responses in Google Forms.
- [x] Document setup, test workflow, safety boundaries, and limitations.
