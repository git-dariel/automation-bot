# TODO - Clinic Sign-up Google Forms Automation System

## UI/UX Pages Implementation

### Phase 1 - Admin Layout and Authentication UI

- [ ] Build the admin login page.
- [ ] Build the admin navigation layout.
- [ ] Add Dashboard, Registration Automation, History & Reports, and Settings navigation.
- [ ] Build reusable loading, empty, and error states.

### Phase 2 - Registration Automation UI

- [ ] Move the existing prototype into the Registration Automation page without changing its functionality.
- [ ] Keep the Google Form URL editable and replaceable at any time without new URL validation.
- [ ] Preserve the existing student input fields and field mappings.
- [ ] Build student add, edit, delete, list, and batch selection UI.
- [ ] Preserve the Auto Fill Only and Auto Fill with Submit toggle.
- [ ] Set the execution button label based on the selected mode.
- [ ] Preserve the existing run progress, results, errors, and Chromium tab behavior.

### Phase 3 - Dashboard UI

- [ ] Build the centralized Dashboard page.
- [ ] Add student count, registration attempt count, and status summary cards.
- [ ] Add latest automation run status and recent activity sections.
- [ ] Add navigation shortcuts to Registration Automation and History & Reports.

### Phase 4 - Registration History and Reports UI

- [ ] Build the Registration History & Reports page.
- [ ] Build a registration attempts table.
- [ ] Add student, date, status, and automation mode filters.
- [ ] Build an attempt details view with timestamps, form URL, and errors.
- [ ] Display form submission status separately from clinic slot confirmation.
- [ ] Add CSV and Excel export controls.

### Phase 5 - Settings UI

- [ ] Build the admin profile and password change forms.
- [ ] Add frontend/backend connection status display.
- [ ] Display read-only automation configuration and browser behavior.

## Backend and Database Implementation

### Phase 6 - MongoDB Setup and Models

- [ ] Add MongoDB support to FastAPI.
- [ ] Load the MongoDB URI provided later from environment variables.
- [ ] Configure the database name and connection lifecycle.
- [ ] Add MongoDB connection health checks.
- [ ] Define admin, student, automation run, and registration attempt document models.
- [ ] Create collection indexes and unique constraints.
- [ ] Implement database access functions and document serialization.
- [ ] Add database startup initialization and error handling.
- [ ] Test MongoDB persistence across backend restarts.

### Phase 7 - Admin Authentication APIs

- [ ] Implement single-admin account initialization.
- [ ] Implement secure password hashing and verification.
- [ ] Implement login, logout, and current-admin endpoints.
- [ ] Implement session/token expiry and protected API access.
- [ ] Implement admin profile update and password change endpoints.

### Phase 8 - Student Management APIs

- [ ] Implement MongoDB-backed student create, list, get, update, and delete endpoints.
- [ ] Preserve the prototype student fields and Google Form mappings.
- [ ] Implement fetching selected saved students for registration runs.
- [ ] Add student API validation and error handling without adding Google Form URL validation.

### Phase 9 - Automation Persistence and Integration

- [ ] Connect selected MongoDB student records to the existing run endpoints.
- [ ] Persist automation run metadata and per-student results to MongoDB.
- [ ] Preserve active-run coordination and duplicate-run prevention.
- [ ] Preserve Auto Fill Only and Auto Fill with Submit behavior.
- [ ] Preserve Google Form URL input behavior and headed Chromium tabs after execution.
- [ ] Record execution timestamps, form URLs, modes, statuses, and errors.
- [ ] Store form submission confirmation separately from clinic slot confirmation.
- [ ] Do not refactor the existing Playwright automation logic.

### Phase 10 - Dashboard and Reporting APIs

- [ ] Implement Dashboard metrics and recent activity endpoints.
- [ ] Implement registration history list and detail endpoints.
- [ ] Implement registration history filtering and pagination.
- [ ] Implement CSV and Excel export endpoints.
- [ ] Implement backend health status endpoint.
- [ ] Add database query and API tests.

## Frontend and API Implementation

### Phase 11 - API Client and Authentication Integration

- [ ] Configure the FastAPI base URL through environment variables.
- [ ] Create a centralized typed API client.
- [ ] Define TypeScript request and response types.
- [ ] Connect admin login, logout, session restoration, and protected routes.
- [ ] Connect admin profile update and password change forms.
- [ ] Handle API authentication errors and expired sessions.

### Phase 12 - Student and Automation API Integration

- [ ] Connect student add, list, edit, delete, and selection UI to FastAPI.
- [ ] Load saved MongoDB student profiles into Registration Automation.
- [ ] Connect the existing Google Form URL and automation mode to run requests.
- [ ] Send selected student records to the existing run workflow.
- [ ] Fetch run progress, execution summaries, and per-student results.
- [ ] Preserve the existing automation behavior and prevent duplicate run requests.
- [ ] Handle loading, network failures, and backend errors in the UI.

### Phase 13 - Dashboard, Reports, and Settings API Integration

- [ ] Connect Dashboard counts, run status, and recent activity to FastAPI.
- [ ] Connect registration history table, filters, pagination, and details.
- [ ] Connect CSV and Excel report downloads.
- [ ] Connect Settings health and backend connection status.
- [ ] Refresh frontend data after student mutations and automation runs.

### Phase 14 - Full-Stack Validation

- [ ] Verify admin login, logout, and protected pages.
- [ ] Verify MongoDB student CRUD and persistence after restart.
- [ ] Verify automation run and attempt history persistence after restart.
- [ ] Verify Dashboard totals, history filters, details, and exports.
- [ ] Verify loading, error, unauthorized, and database outage states.
- [ ] Regression-test Auto Fill Only with the owned test form.
- [ ] Regression-test Auto Fill with Submit with the owned test form.
- [ ] Verify Chromium tabs remain open after both modes.
- [ ] Verify the Google Form URL behavior and student field mappings remain unchanged.
- [ ] Verify concurrency protection and student data isolation.
- [ ] Run frontend lint, type-check, and production build.
- [ ] Run backend automated tests.
- [ ] Document MongoDB environment variables and local startup instructions.

## Completed MVP Tasks (Preserved)

### Phase 15 - MVP Setup

- [x] Use the existing Next.js TypeScript and Tailwind CSS app.
- [x] Initialize the FastAPI backend structure.
- [x] Add Playwright Python and Chromium setup instructions.
- [x] Verify the current Google Form and its clinic sign-up fields.
- [x] Prepare ten fabricated clinician profiles.

### Phase 16 - MVP Frontend

- [x] Add an editable Google Form URL input.
- [x] Display ten sample clinician profiles.
- [x] Add the Start Test action and duplicate-run prevention.
- [x] Add the Test Submit switch, off by default, with confirmation.
- [x] Display run summary, execution time, and per-profile statuses.
- [x] Handle API validation, conflict, and network errors.
- [x] Use an explicit light theme with accessible contrast.
- [x] Open ten prefilled inspection tabs from the deployed frontend when using the cloud API.

### Phase 17 - MVP Backend

- [x] Implement `POST /test-runs`.
- [x] Implement `GET /test-runs/{job_id}`.
- [x] Add in-memory job state and thread-safe progress tracking.
- [x] Accept any well-formed public Google Forms URL without an exact form-ID allowlist.
- [x] Reject simultaneous active browser runs.
- [x] Configure local frontend CORS without wildcard origins.

### Phase 18 - MVP Automation

- [x] Launch headed Chromium locally.
- [x] Open ten tabs for the selected test form.
- [x] Assign one fabricated clinician profile per tab.
- [x] Fill and verify email, text, and radio fields by visible label.
- [x] Implement optional form submission.
- [x] Detect the Google Forms confirmation page and capture safe errors.
- [x] Keep fill-only and submitted confirmation tabs open until Chromium is closed manually.

### Phase 19 - MVP Tests

- [x] Run frontend lint, type-check, and production build after the clinic form migration.
- [x] Run the backend automated test suite after the clinic form migration.
- [x] Run a live fill-only test with ten visible tabs.
- [x] Confirm ten-tab concurrency and profile data isolation live.
- [x] Validate generated prefill URLs against the live Google Form without submitting responses.
- [ ] Run an intentional submission test with ten responses on an owned test form.
- [ ] Verify ten distinct responses in the owned Google Form.
- [x] Document setup, test workflow, safety boundaries, and limitations.
