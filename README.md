# Clinic Sign-up Automation Prototype

A local proof of concept that uses a Next.js dashboard, FastAPI, and headed Playwright Chromium to fill ten copies of a public Google Form with fabricated clinician schedule data.

The **Test Submit** switch is off by default. Successful fill-only and submission runs keep Chromium open for inspection and finish when you close the browser. Use this project only with forms you own or are authorized to automate.

## Requirements

- Node.js and pnpm 10
- Python 3.12
- A desktop session where headed Chromium can open

## Setup (PowerShell)

From the repository root:

```powershell
pnpm install
py -m venv backend\.venv
backend\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
python -m playwright install chromium
Copy-Item .env.example .env.local
Copy-Item backend\.env.example backend\.env
```

The checked-in example values target the supplied Clinic Sign Up Form. They are public identifiers, not credentials. The dashboard accepts a public `forms.gle` short link or canonical `docs.google.com/forms` link, so the configured form can be changed without updating an allowlisted form ID.

## Run locally

From the `backend` directory, start FastAPI in one PowerShell terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000 --env-file .env
```

From the repository root, start Next.js in another terminal:

```powershell
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000). Keep **Test Submit** disabled for the first run. When all profiles show `ready`, inspect the ten tabs and close Chromium to complete the job.

## Configuration

Frontend (`.env.local`):

- `NEXT_PUBLIC_API_BASE_URL`: FastAPI base URL.
- `NEXT_PUBLIC_GOOGLE_FORM_URL`: initial URL shown in the dashboard.

Backend (`backend/.env`):

- `FRONTEND_ORIGIN`: permitted browser origin for CORS.
- `GOOGLE_FORM_URL`: default public Google Form URL.
- `PLAYWRIGHT_TIMEOUT_MS`: per-action timeout.
- `PLAYWRIGHT_HEADLESS`: launches Chromium without a visible window when `true`.
- `KEEP_BROWSER_OPEN`: waits for manual browser closure when `true`.
- `PLAYWRIGHT_MAX_CONCURRENT_PAGES`: limits simultaneous pages in auto-closing mode.

Local defaults are `PLAYWRIGHT_HEADLESS=false` and `KEEP_BROWSER_OPEN=true`. The Heroku deployment uses the inverse because a dyno has no visible desktop and cannot wait for a user to close browser tabs.

## Heroku backend

The repository root contains the Heroku `Procfile`, Python version, Python dependency entrypoint, Chromium packages, and browser installation hook. The deployed service runs only the FastAPI backend. Its in-memory run history is cleared whenever the dyno restarts.

Heroku must use these runtime values:

```text
FRONTEND_ORIGIN=http://localhost:3000
GOOGLE_FORM_URL=https://forms.gle/4Qn7MCvAzMBrR1Hw7
PLAYWRIGHT_TIMEOUT_MS=30000
PLAYWRIGHT_HEADLESS=true
KEEP_BROWSER_OPEN=false
PLAYWRIGHT_BROWSERS_PATH=0
PLAYWRIGHT_MAX_CONCURRENT_PAGES=1
WEB_CONCURRENCY=1
```

The remote backend fills or submits one profile at a time in headless Chromium and closes each page after completion. This keeps the ten-profile run within the memory available to the Basic dyno. Keep submission disabled unless responses are deliberately intended.

Do not commit real credentials or student data.

## Checks

```powershell
pnpm lint
pnpm exec tsc --noEmit
pnpm build
backend\.venv\Scripts\python.exe -m pytest backend\tests -q
```

API documentation is available at [http://localhost:8000/docs](http://localhost:8000/docs) while FastAPI is running.
