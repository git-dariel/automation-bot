import pytest

from backend.app.job_store import ActiveRunError, JobStore
from backend.app.models import EmployeeStatus, RunStatus
from backend.app.profiles import build_sample_profiles


def test_tracks_isolated_employee_results_and_summary():
    store = JobStore()
    profiles = build_sample_profiles()
    job = store.create(False, profiles)

    store.mark_running(job.id)
    store.update_employee(job.id, profiles[0].id, EmployeeStatus.READY)
    store.update_employee(job.id, profiles[1].id, EmployeeStatus.FAILED, "Safe error")
    result = store.get(job.id)

    assert result is not None
    assert result.summary.ready == 1
    assert result.summary.failed == 1
    assert result.summary.filling == 0
    assert result.results[0].student_number == "TEST-2026-001"
    assert result.results[1].error == "Safe error"
    assert len({clinician.student_number for clinician in result.results}) == 10


def test_allows_only_one_active_run_until_finished():
    store = JobStore()
    profiles = build_sample_profiles()
    first = store.create(False, profiles)

    with pytest.raises(ActiveRunError):
        store.create(False, profiles)

    store.finish(first.id, RunStatus.COMPLETED, 120)
    second = store.create(False, profiles)
    assert second.id != first.id
