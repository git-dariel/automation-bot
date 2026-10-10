from fastapi.testclient import TestClient

from backend.app import main
from backend.app.models import EmployeeStatus, RunStatus


client = TestClient(main.app)


def complete_without_browser(job_id, form_url, submit, profiles, store, settings):
    del form_url, submit, settings
    store.mark_running(job_id)
    for profile in profiles:
        store.update_employee(job_id, profile.id, EmployeeStatus.READY)
    store.finish(job_id, RunStatus.COMPLETED, 42)


def leave_pending(job_id, form_url, submit, profiles, store, settings):
    del job_id, form_url, submit, profiles, store, settings


def fail_without_leaking_details(job_id, form_url, submit, profiles, store, settings):
    del form_url, submit, settings
    store.mark_running(job_id)
    for profile in profiles:
        store.update_employee(job_id, profile.id, EmployeeStatus.FAILED, "Safe test failure.")
    store.finish(job_id, RunStatus.FAILED, 11, "Safe test failure.")


def test_create_and_get_completed_run(monkeypatch):
    monkeypatch.setattr(main, "run_automation_job", complete_without_browser)
    response = client.post(
        "/test-runs",
        json={"form_url": main.settings.google_form_url, "submit": False},
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]
    result = client.get(f"/test-runs/{job_id}")
    assert result.status_code == 200
    assert result.json()["status"] == "completed"
    assert result.json()["summary"]["ready"] == 10
    assert result.json()["execution_ms"] == 42


def test_rejects_non_google_form(monkeypatch):
    monkeypatch.setattr(main, "run_automation_job", complete_without_browser)
    response = client.post(
        "/test-runs",
        json={"form_url": "https://example.com/not-a-google-form", "submit": False},
    )
    assert response.status_code == 422
    assert "Google Forms" in response.json()["detail"]


def test_rejects_second_active_run(monkeypatch):
    monkeypatch.setattr(main, "run_automation_job", leave_pending)
    first = client.post(
        "/test-runs",
        json={"form_url": main.settings.google_form_url, "submit": False},
    )
    second = client.post(
        "/test-runs",
        json={"form_url": main.settings.google_form_url, "submit": False},
    )
    assert first.status_code == 202
    assert second.status_code == 409


def test_returns_safe_failure_state(monkeypatch):
    monkeypatch.setattr(main, "run_automation_job", fail_without_leaking_details)
    response = client.post(
        "/test-runs",
        json={"form_url": main.settings.google_form_url, "submit": True},
    )
    result = client.get(f"/test-runs/{response.json()['job_id']}").json()
    assert result["status"] == "failed"
    assert result["summary"]["failed"] == 10
    assert result["error"] == "Safe test failure."


def test_unknown_run_returns_not_found():
    response = client.get("/test-runs/not-a-job")
    assert response.status_code == 404
    assert response.json()["detail"] == "Test run not found."
