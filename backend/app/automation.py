import asyncio
import re
import sys
from time import perf_counter

from playwright.async_api import (
    Browser,
    BrowserContext,
    Locator,
    Page,
    async_playwright,
    expect,
)

from .config import Settings
from .job_store import JobStore
from .models import ClinicianProfile, EmployeeStatus, RunStatus


SAFE_AUTOMATION_ERROR = "The form could not be completed. Check its accessibility and field labels."
SHIFT_SCHEDULE_LABEL = (
    "Shift Schedule ( Saturdays are am pm only, so please use 8-12 and 12-4pm "
    "as substitute for 1-5pm)"
)


async def _question(page: Page, label: str) -> Locator:
    heading = page.locator('[role="heading"]').filter(
        has_text=re.compile(rf"^{re.escape(label)}\s*\*?$", re.IGNORECASE),
    )
    question = page.locator('[role="listitem"]').filter(has=heading)
    await question.wait_for(state="visible")
    return question


async def _fill_text(
    page: Page,
    label: str,
    value: str,
    *,
    input_type: str = "text",
) -> None:
    question = await _question(page, label)
    field = question.locator(f'input[type="{input_type}"]').first
    await field.fill(value)
    if await field.input_value() != value:
        raise RuntimeError(f"Verification failed for {label}.")


async def _fill_radio(page: Page, label: str, value: str) -> None:
    question = await _question(page, label)
    option = question.get_by_role("radio", name=value, exact=True)
    await option.click()
    await expect(option).to_have_attribute("aria-checked", "true")


async def _submit(page: Page) -> None:
    await page.get_by_role("button", name="Submit", exact=True).click()
    await page.wait_for_url("**/formResponse", wait_until="domcontentloaded")
    await page.locator(".vHW8K").wait_for(state="visible")


async def _process_employee(
    page: Page,
    profile: ClinicianProfile,
    form_url: str,
    submit: bool,
    job_id: str,
    store: JobStore,
) -> None:
    store.update_employee(job_id, profile.id, EmployeeStatus.FILLING)
    try:
        await page.goto(form_url, wait_until="domcontentloaded")
        await _fill_text(page, "Email", profile.email, input_type="email")
        await _fill_text(page, "Name of Clinician", profile.clinician_name)
        await _fill_text(page, "Student Number", profile.student_number)
        await _fill_radio(page, "Scheduled Day", profile.scheduled_day)
        await _fill_radio(page, SHIFT_SCHEDULE_LABEL, profile.shift_schedule)
        await _fill_radio(
            page,
            "Department / Procedure to do",
            profile.department,
        )
        await _fill_radio(
            page,
            "Time Interval Required",
            profile.time_interval,
        )
        store.update_employee(job_id, profile.id, EmployeeStatus.READY)
        if submit:
            await _submit(page)
            store.update_employee(job_id, profile.id, EmployeeStatus.SUBMITTED)
    except Exception:
        store.update_employee(
            job_id,
            profile.id,
            EmployeeStatus.FAILED,
            SAFE_AUTOMATION_ERROR,
        )


async def _wait_for_manual_close(browser: Browser, context: BrowserContext) -> None:
    while browser.is_connected():
        if not context.pages:
            await browser.close()
            return
        await asyncio.sleep(0.25)


async def _process_with_managed_page(
    context: BrowserContext,
    semaphore: asyncio.Semaphore,
    profile: ClinicianProfile,
    form_url: str,
    submit: bool,
    job_id: str,
    store: JobStore,
) -> None:
    async with semaphore:
        page = await context.new_page()
        try:
            await _process_employee(page, profile, form_url, submit, job_id, store)
        finally:
            if not page.is_closed():
                await page.close()


async def _run(
    job_id: str,
    form_url: str,
    submit: bool,
    profiles: list[ClinicianProfile],
    store: JobStore,
    settings: Settings,
) -> None:
    started = perf_counter()
    browser: Browser | None = None
    store.mark_running(job_id)

    try:
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(
                headless=settings.playwright_headless,
                chromium_sandbox=False,
            )
            context = await browser.new_context(locale="en-US")
            context.set_default_timeout(settings.playwright_timeout_ms)
            if settings.keep_browser_open:
                pages = [await context.new_page() for _ in profiles]
                await asyncio.gather(
                    *(
                        _process_employee(page, profile, form_url, submit, job_id, store)
                        for page, profile in zip(pages, profiles, strict=True)
                    )
                )
            else:
                semaphore = asyncio.Semaphore(settings.playwright_max_concurrent_pages)
                await asyncio.gather(
                    *(
                        _process_with_managed_page(
                            context,
                            semaphore,
                            profile,
                            form_url,
                            submit,
                            job_id,
                            store,
                        )
                        for profile in profiles
                    )
                )
            execution_ms = round((perf_counter() - started) * 1000)
            result = store.get(job_id)
            has_success = bool(
                result and (result.summary.ready > 0 or result.summary.submitted > 0)
            )
            has_failure = bool(result and result.summary.failed > 0)

            if has_success:
                store.mark_ready(job_id, execution_ms)
                if settings.keep_browser_open:
                    await _wait_for_manual_close(browser, context)
                else:
                    await browser.close()
                    browser = None
                store.finish(
                    job_id,
                    RunStatus.FAILED if has_failure else RunStatus.COMPLETED,
                    execution_ms,
                    SAFE_AUTOMATION_ERROR if has_failure else None,
                )
                return

            await browser.close()
            browser = None
            store.finish(
                job_id,
                RunStatus.FAILED if has_failure or not has_success else RunStatus.COMPLETED,
                execution_ms,
                SAFE_AUTOMATION_ERROR if has_failure or not has_success else None,
            )
    except Exception:
        execution_ms = round((perf_counter() - started) * 1000)
        if browser and browser.is_connected():
            await browser.close()
        result = store.get(job_id)
        if result:
            for employee in result.results:
                if employee.status in {EmployeeStatus.PENDING, EmployeeStatus.FILLING}:
                    store.update_employee(
                        job_id,
                        employee.id,
                        EmployeeStatus.FAILED,
                        SAFE_AUTOMATION_ERROR,
                    )
        store.finish(job_id, RunStatus.FAILED, execution_ms, SAFE_AUTOMATION_ERROR)


def run_automation_job(
    job_id: str,
    form_url: str,
    submit: bool,
    profiles: list[ClinicianProfile],
    store: JobStore,
    settings: Settings,
) -> None:
    # Uvicorn's Windows reload process uses a Selector event-loop policy.
    # Playwright launches a driver subprocess, which requires a Proactor loop.
    loop = (
        asyncio.ProactorEventLoop()
        if sys.platform == "win32"
        else asyncio.new_event_loop()
    )
    try:
        asyncio.set_event_loop(loop)
        loop.run_until_complete(
            _run(job_id, form_url, submit, profiles, store, settings)
        )
        loop.run_until_complete(loop.shutdown_asyncgens())
    finally:
        asyncio.set_event_loop(None)
        loop.close()
