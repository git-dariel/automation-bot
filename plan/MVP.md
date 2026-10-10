# Google Forms Clinic Sign-up Automation - MVP

## Goal

Validate that a local web app can open ten tabs of an owned Google Form, fill each tab with a different fabricated clinician schedule, verify the values, and optionally submit test responses.

This is a proof of concept, not a production scheduling system or a way to bypass Google protections.

## Stack

- **Frontend:** Next.js 16, TypeScript, Tailwind CSS 4
- **Backend:** FastAPI on Python 3.12
- **Automation:** Playwright for Python with headed Chromium
- **Storage:** In-memory job state; no database

## Current Test Form

- Public URL: `https://forms.gle/4Qn7MCvAzMBrR1Hw7`
- Title: **Clinic Sign Up Form (Oct. 5-10, 2026)**

| Field | Type / supported values |
| --- | --- |
| Email | Email |
| Name of Clinician | Short answer |
| Student Number | Short answer |
| Scheduled Day | Monday through Friday for the ten sample profiles |
| Shift Schedule | 8-12 AM shift, 12-4 PM shift, 4-8 PM shift, 7-11AM shift (sundays), 11-3 PM shift (sundays) |
| Department / Procedure to do | OD / OP, Prothodontics, Endodontics, Operative Dentistry, Periodontics, Oral Sugery, Orthodontics, Pediatrics, TYPO |
| Time Interval Required | 4 hrs, 2hrs, 1hr |

The backend accepts public HTTPS `forms.gle` short links and canonical `docs.google.com/forms` links. It no longer restricts runs to one configured form ID. Non-Google and malformed URLs remain rejected for safety.

## MVP Features

1. Single-page dashboard with an editable Google Form URL.
2. Ten fabricated clinician profiles with unique test student numbers.
3. Start Test action with duplicate-run prevention.
4. Test Submit switch that is off by default and requires confirmation when enabled.
5. FastAPI job creation and polling endpoints.
6. A headed Playwright worker opening one isolated tab per profile.
7. Label-based mapping for email, text, and radio fields.
8. Value verification before a profile becomes ready or submitted.
9. Per-profile progress, safe errors, summary counts, and execution time.
10. Tabs remain open after filling or submission until Chromium is manually closed.

## User Flow

1. Start FastAPI and Next.js locally.
2. Review or change the Google Form URL and the ten fabricated profiles.
3. Leave Test Submit off and click **Start test**.
4. Chromium opens ten tabs and fills one independent profile in each.
5. The dashboard reports filling, ready, and failed states.
6. Inspect the ready tabs, then close Chromium to finish the run.
7. Only when intentional, enable Test Submit, accept the confirmation, and verify the ten responses in Google Forms.

## API

### `POST /test-runs`

Request:

```json
{ "form_url": "https://forms.gle/4Qn7MCvAzMBrR1Hw7", "submit": false }
```

Returns `202` with a job ID. Returns `409` while another browser run is active and `422` for a malformed or non-Google Forms URL.

### `GET /test-runs/{job_id}`

Returns run status, timestamps, execution time, summary counts, and all ten profile results. Run states are `pending`, `running`, `ready`, `completed`, and `failed`. Profile states are `pending`, `filling`, `ready`, `submitted`, and `failed`.

## Acceptance Criteria

- Ten headed Chromium tabs open the selected Google Form.
- All ten fabricated profiles populate and verify the correct fields without data mixing.
- Fill-only runs never click Submit and remain visible for inspection.
- Submission occurs only after the user enables the switch and confirms the warning.
- Successful submission is reported only after the Google Forms confirmation page appears.
- Submitted confirmation tabs remain open for inspection until Chromium is closed manually.
- Failures are captured with safe UI errors and never reported as successful.
- A second run cannot start until the current browser session closes.

## Out of Scope

- Real student data, authentication, database storage, approvals, or administration
- Hosting, scheduling, scaling, retry orchestration, or multiple simultaneous runs
- CAPTCHA bypass, stealth techniques, proxy rotation, or third-party form automation
