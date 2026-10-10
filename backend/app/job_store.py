from copy import deepcopy
from datetime import datetime, timezone
from threading import Lock
from uuid import uuid4

from .models import (
    ClinicianProfile,
    ClinicianResult,
    EmployeeStatus,
    RunStatus,
    RunSummary,
    TestRunResponse,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ActiveRunError(RuntimeError):
    pass


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, TestRunResponse] = {}
        self._active_job_id: str | None = None
        self._lock = Lock()

    def create(self, submit: bool, profiles: list[ClinicianProfile]) -> TestRunResponse:
        with self._lock:
            if self._active_job_id is not None:
                raise ActiveRunError("Close the active Chromium test before starting another run.")

            job_id = str(uuid4())
            results = [ClinicianResult(**profile.model_dump()) for profile in profiles]
            job = TestRunResponse(
                id=job_id,
                status=RunStatus.PENDING,
                submit=submit,
                created_at=utc_now(),
                summary=self._summary(results),
                results=results,
            )
            self._jobs[job_id] = job
            self._active_job_id = job_id
            return deepcopy(job)

    def get(self, job_id: str) -> TestRunResponse | None:
        with self._lock:
            job = self._jobs.get(job_id)
            if job is None:
                return None
            job.summary = self._summary(job.results)
            return deepcopy(job)

    def mark_running(self, job_id: str) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = RunStatus.RUNNING
            job.started_at = utc_now()

    def update_employee(
        self,
        job_id: str,
        profile_id: str,
        status: EmployeeStatus,
        error: str | None = None,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            result = next(item for item in job.results if item.id == profile_id)
            result.status = status
            result.error = error
            job.summary = self._summary(job.results)

    def mark_ready(self, job_id: str, execution_ms: int) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = RunStatus.READY
            job.execution_ms = execution_ms
            job.finished_at = utc_now()

    def finish(
        self,
        job_id: str,
        status: RunStatus,
        execution_ms: int | None = None,
        error: str | None = None,
    ) -> None:
        with self._lock:
            job = self._jobs[job_id]
            job.status = status
            job.execution_ms = execution_ms if execution_ms is not None else job.execution_ms
            job.finished_at = job.finished_at or utc_now()
            job.error = error
            if self._active_job_id == job_id:
                self._active_job_id = None

    def clear(self) -> None:
        with self._lock:
            self._jobs.clear()
            self._active_job_id = None

    @staticmethod
    def _summary(results: list[ClinicianResult]) -> RunSummary:
        counts = {status: 0 for status in EmployeeStatus}
        for result in results:
            counts[result.status] += 1
        return RunSummary(
            total=len(results),
            pending=counts[EmployeeStatus.PENDING],
            filling=counts[EmployeeStatus.FILLING],
            ready=counts[EmployeeStatus.READY],
            submitted=counts[EmployeeStatus.SUBMITTED],
            failed=counts[EmployeeStatus.FAILED],
        )
