from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field, HttpUrl


class EmployeeStatus(StrEnum):
    PENDING = "pending"
    FILLING = "filling"
    READY = "ready"
    SUBMITTED = "submitted"
    FAILED = "failed"


class RunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    READY = "ready"
    COMPLETED = "completed"
    FAILED = "failed"


class ClinicianProfile(BaseModel):
    id: str
    email: str
    clinician_name: str
    student_number: str
    scheduled_day: str
    shift_schedule: str
    department: str
    time_interval: str


class ClinicianResult(ClinicianProfile):
    status: EmployeeStatus = EmployeeStatus.PENDING
    error: str | None = None


class TestRunCreate(BaseModel):
    form_url: HttpUrl
    submit: bool = False


class TestRunCreated(BaseModel):
    job_id: str
    status: RunStatus
    prefill_urls: list[HttpUrl] = Field(default_factory=list)


class RunSummary(BaseModel):
    total: int
    pending: int
    filling: int
    ready: int
    submitted: int
    failed: int


class TestRunResponse(BaseModel):
    id: str
    status: RunStatus
    submit: bool
    created_at: datetime
    started_at: datetime | None = None
    finished_at: datetime | None = None
    execution_ms: int | None = Field(default=None, ge=0)
    error: str | None = None
    summary: RunSummary
    results: list[ClinicianResult]
