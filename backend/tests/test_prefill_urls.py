import html
import json
from urllib.parse import parse_qs, urlsplit

import pytest

from backend.app import prefill_urls
from backend.app.form_fields import (
    CLINICIAN_NAME_LABEL,
    DEPARTMENT_LABEL,
    SCHEDULED_DAY_LABEL,
    SHIFT_SCHEDULE_LABEL,
    STUDENT_NUMBER_LABEL,
    TIME_INTERVAL_LABEL,
)
from backend.app.profiles import build_sample_profiles


CANONICAL_FORM_URL = (
    "https://docs.google.com/forms/d/e/"
    "1FAIpQLSdIhnVni_CctGJC0maz-GjVVYgMd-b9oWiTK5q9RYfP0qz0-w/viewform"
)


class FakeResponse:
    def __init__(self, url: str, text: str) -> None:
        self.url = url
        self.text = text

    def raise_for_status(self) -> None:
        return None


def _form_html(labels: list[str]) -> str:
    controls = []
    for entry_id, label in enumerate(labels, start=100):
        params = [entry_id, label, None, 0, [[entry_id, None, True]]]
        # Google appends additional values after the first JSON array.
        value = html.escape(f'%.@.{json.dumps(params)},"control-id"', quote=True)
        controls.append(f'<div data-params="{value}"></div>')
    return "".join(controls)


def test_builds_one_prefilled_url_per_profile(monkeypatch):
    labels = [
        CLINICIAN_NAME_LABEL,
        STUDENT_NUMBER_LABEL,
        SCHEDULED_DAY_LABEL,
        SHIFT_SCHEDULE_LABEL,
        DEPARTMENT_LABEL,
        TIME_INTERVAL_LABEL,
    ]
    page_html = _form_html(labels)
    monkeypatch.setattr(
        prefill_urls.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse(CANONICAL_FORM_URL, page_html),
    )

    profiles = build_sample_profiles()
    urls = prefill_urls.build_prefill_urls("https://forms.gle/example", profiles)

    assert len(urls) == len(profiles) == 10
    query = parse_qs(urlsplit(urls[0]).query)
    assert query["emailAddress"] == [profiles[0].email]
    assert query["entry.100"] == [profiles[0].clinician_name]
    assert query["entry.101"] == [profiles[0].student_number]
    assert query["entry.102"] == [profiles[0].scheduled_day]
    assert query["entry.103"] == [profiles[0].shift_schedule]
    assert query["entry.104"] == [profiles[0].department]
    assert query["entry.105"] == [profiles[0].time_interval]


def test_rejects_form_when_a_required_field_is_missing(monkeypatch):
    page_html = _form_html([CLINICIAN_NAME_LABEL])
    monkeypatch.setattr(
        prefill_urls.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse(CANONICAL_FORM_URL, page_html),
    )

    with pytest.raises(prefill_urls.PrefillUrlError, match="Visible tabs"):
        prefill_urls.build_prefill_urls(
            "https://forms.gle/example",
            build_sample_profiles(),
        )


def test_rejects_redirect_outside_google_forms(monkeypatch):
    monkeypatch.setattr(
        prefill_urls.httpx,
        "get",
        lambda *args, **kwargs: FakeResponse("https://example.com/viewform", ""),
    )

    with pytest.raises(prefill_urls.PrefillUrlError, match="Visible tabs"):
        prefill_urls.build_prefill_urls(
            "https://forms.gle/example",
            build_sample_profiles(),
        )
