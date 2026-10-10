from dataclasses import dataclass
import os


DEFAULT_FORM_URL = "https://forms.gle/4Qn7MCvAzMBrR1Hw7"


@dataclass(frozen=True)
class Settings:
    frontend_origin: str
    google_form_url: str
    playwright_timeout_ms: int


def get_settings() -> Settings:
    return Settings(
        frontend_origin=os.getenv("FRONTEND_ORIGIN", "http://localhost:3000"),
        google_form_url=os.getenv("GOOGLE_FORM_URL", DEFAULT_FORM_URL),
        playwright_timeout_ms=int(os.getenv("PLAYWRIGHT_TIMEOUT_MS", "30000")),
    )
