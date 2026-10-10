import asyncio
import sys

from backend.app import automation
from backend.app.job_store import JobStore
from backend.app.models import EmployeeStatus
from backend.app.profiles import build_sample_profiles


class FakePage:
    async def goto(self, form_url: str, wait_until: str) -> None:
        assert form_url.startswith("https://forms.gle/")
        assert wait_until == "domcontentloaded"


class FakeBrowser:
    def __init__(self, connected: bool = True) -> None:
        self.connected = connected
        self.was_closed = False

    def is_connected(self) -> bool:
        return self.connected

    async def close(self) -> None:
        self.was_closed = True
        self.connected = False

    async def new_context(self, locale: str):
        assert locale == "en-US"
        self.context = FakeContext([FakePage()])
        return self.context


class FakeContext:
    def __init__(self, pages) -> None:
        self.pages = pages

    def set_default_timeout(self, timeout: int) -> None:
        assert timeout > 0

    async def new_page(self):
        page = FakePage()
        self.pages.append(page)
        return page


class FakeChromium:
    def __init__(self, browser: FakeBrowser) -> None:
        self.browser = browser

    async def launch(self, headless: bool, chromium_sandbox: bool):
        assert headless is self.expected_headless
        assert chromium_sandbox is False
        return self.browser

    @property
    def expected_headless(self) -> bool:
        return getattr(self.browser, "expected_headless", False)


class FakePlaywrightManager:
    def __init__(self, browser: FakeBrowser) -> None:
        self.playwright = type(
            "FakePlaywright",
            (),
            {"chromium": FakeChromium(browser)},
        )()

    async def __aenter__(self):
        return self.playwright

    async def __aexit__(self, exc_type, exc, traceback):
        del exc_type, exc, traceback


async def noop(*args, **kwargs) -> None:
    del args, kwargs


def prepare_job():
    store = JobStore()
    profile = build_sample_profiles()[0]
    job = store.create(False, [profile])
    store.mark_running(job.id)
    return store, job, profile


def install_successful_fields(monkeypatch):
    monkeypatch.setattr(automation, "_fill_text", noop)
    monkeypatch.setattr(automation, "_fill_radio", noop)


def test_process_employee_reaches_ready_after_verified_fields(monkeypatch):
    store, job, profile = prepare_job()
    install_successful_fields(monkeypatch)

    asyncio.run(
        automation._process_employee(
            FakePage(), profile, "https://forms.gle/approved", False, job.id, store
        )
    )

    result = store.get(job.id)
    assert result is not None
    assert result.results[0].status == EmployeeStatus.READY
    assert result.results[0].error is None


def test_process_employee_captures_fill_or_verification_failure(monkeypatch):
    store, job, profile = prepare_job()

    async def fail_fill(*args, **kwargs):
        del args, kwargs
        raise RuntimeError("Internal locator details")

    monkeypatch.setattr(automation, "_fill_text", fail_fill)

    asyncio.run(
        automation._process_employee(
            FakePage(), profile, "https://forms.gle/approved", False, job.id, store
        )
    )

    result = store.get(job.id)
    assert result is not None
    assert result.results[0].status == EmployeeStatus.FAILED
    assert result.results[0].error == automation.SAFE_AUTOMATION_ERROR
    assert "locator" not in result.results[0].error


def test_process_employee_captures_submission_confirmation_failure(monkeypatch):
    store, job, profile = prepare_job()
    install_successful_fields(monkeypatch)

    async def fail_submit(*args, **kwargs):
        del args, kwargs
        raise RuntimeError("Confirmation selector changed")

    monkeypatch.setattr(automation, "_submit", fail_submit)

    asyncio.run(
        automation._process_employee(
            FakePage(), profile, "https://forms.gle/approved", True, job.id, store
        )
    )

    result = store.get(job.id)
    assert result is not None
    assert result.results[0].status == EmployeeStatus.FAILED
    assert result.results[0].error == automation.SAFE_AUTOMATION_ERROR


def test_worker_uses_subprocess_capable_loop_on_windows(monkeypatch):
    observed_loop = None

    async def capture_loop(*args, **kwargs):
        nonlocal observed_loop
        del args, kwargs
        observed_loop = asyncio.get_running_loop()

    monkeypatch.setattr(automation, "_run", capture_loop)
    automation.run_automation_job("job", "url", False, [], None, None)

    assert observed_loop is not None
    if sys.platform == "win32":
        assert isinstance(observed_loop, asyncio.ProactorEventLoop)


def test_manual_close_finishes_when_all_tabs_are_closed():
    browser = FakeBrowser()
    context = FakeContext([])

    asyncio.run(automation._wait_for_manual_close(browser, context))

    assert browser.was_closed is True
    assert browser.is_connected() is False


def test_submitted_tabs_wait_for_manual_close(monkeypatch):
    store = JobStore()
    profile = build_sample_profiles()[0]
    job = store.create(True, [profile])
    browser = FakeBrowser()
    waited_for_close = False

    async def submit_profile(page, current_profile, form_url, submit, job_id, job_store):
        del page, form_url
        assert submit is True
        job_store.update_employee(job_id, current_profile.id, EmployeeStatus.SUBMITTED)

    async def record_manual_wait(current_browser, context):
        nonlocal waited_for_close
        assert current_browser is browser
        assert context.pages
        waited_for_close = True

    monkeypatch.setattr(
        automation,
        "async_playwright",
        lambda: FakePlaywrightManager(browser),
    )
    monkeypatch.setattr(automation, "_process_employee", submit_profile)
    monkeypatch.setattr(automation, "_wait_for_manual_close", record_manual_wait)

    asyncio.run(
        automation._run(
            job.id,
            "https://forms.gle/approved",
            True,
            [profile],
            store,
            type(
                "Settings",
                (),
                {
                    "playwright_timeout_ms": 1000,
                    "playwright_headless": False,
                    "keep_browser_open": True,
                },
            )(),
        )
    )

    result = store.get(job.id)
    assert result is not None
    assert waited_for_close is True
    assert browser.was_closed is False
    assert result.status.value == "completed"
    assert result.summary.submitted == 1


def test_headless_run_closes_browser_without_manual_wait(monkeypatch):
    store = JobStore()
    profile = build_sample_profiles()[0]
    job = store.create(False, [profile])
    browser = FakeBrowser()
    browser.expected_headless = True

    async def ready_profile(page, current_profile, form_url, submit, job_id, job_store):
        del page, form_url
        assert submit is False
        job_store.update_employee(job_id, current_profile.id, EmployeeStatus.READY)

    async def unexpected_manual_wait(*args, **kwargs):
        del args, kwargs
        raise AssertionError("Headless deployment runs must not wait for manual close.")

    monkeypatch.setattr(
        automation,
        "async_playwright",
        lambda: FakePlaywrightManager(browser),
    )
    monkeypatch.setattr(automation, "_process_employee", ready_profile)
    monkeypatch.setattr(automation, "_wait_for_manual_close", unexpected_manual_wait)

    asyncio.run(
        automation._run(
            job.id,
            "https://forms.gle/approved",
            False,
            [profile],
            store,
            type(
                "Settings",
                (),
                {
                    "playwright_timeout_ms": 1000,
                    "playwright_headless": True,
                    "keep_browser_open": False,
                },
            )(),
        )
    )

    result = store.get(job.id)
    assert result is not None
    assert browser.was_closed is True
    assert result.status.value == "completed"
