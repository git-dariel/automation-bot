from fastapi import BackgroundTasks, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .automation import run_automation_job
from .config import get_settings
from .form_urls import FormUrlError, validate_form_url
from .job_store import ActiveRunError, JobStore
from .models import TestRunCreate, TestRunCreated, TestRunResponse
from .prefill_urls import PrefillUrlError, build_prefill_urls
from .profiles import build_sample_profiles


settings = get_settings()
store = JobStore()

app = FastAPI(
    title="Clinic Sign-up Automation API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/test-runs",
    response_model=TestRunCreated,
    status_code=status.HTTP_202_ACCEPTED,
)
def create_test_run(
    request: TestRunCreate,
    background_tasks: BackgroundTasks,
) -> TestRunCreated:
    form_url = str(request.form_url)
    try:
        validate_form_url(form_url)
        profiles = build_sample_profiles()
        prefill_urls = (
            build_prefill_urls(form_url, profiles)
            if not settings.keep_browser_open
            else []
        )
        job = store.create(request.submit, profiles)
    except (FormUrlError, PrefillUrlError) as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
    except ActiveRunError as error:
        raise HTTPException(status_code=409, detail=str(error)) from error

    background_tasks.add_task(
        run_automation_job,
        job.id,
        form_url,
        request.submit,
        profiles,
        store,
        settings,
    )
    return TestRunCreated(
        job_id=job.id,
        status=job.status,
        prefill_urls=prefill_urls,
    )


@app.get("/test-runs/{job_id}", response_model=TestRunResponse)
def get_test_run(job_id: str) -> TestRunResponse:
    job = store.get(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Test run not found.")
    return job
