from dataclasses import dataclass
import os


DEFAULT_FORM_URL = "https://forms.gle/4Qn7MCvAzMBrR1Hw7"


def _read_bool(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    frontend_origin: str
    google_form_url: str
    playwright_timeout_ms: int
    playwright_headless: bool
    keep_browser_open: bool
    playwright_max_concurrent_pages: int


def get_settings() -> Settings:
    return Settings(
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
        google_form_url=os.getenv("GOOGLE_FORM_URL", DEFAULT_FORM_URL),
        playwright_timeout_ms=int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000")),
        playwright_headless=_read_bool("PLAYWRIGHT_HEADLESS", False),
        keep_browser_open=_read_bool("KEEP_BROWSER_OPEN", True),
        playwright_max_concurrent_pages=max(
            1,
            int(os.getenv("PLAYWRIGHT_MAX_CONCURRENT_PAGES", "10")),
        ),
    )
