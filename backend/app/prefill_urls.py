import html
import json
import re
from urllib.parse import urlencode, urlsplit, urlunsplit

import httpx

from .form_fields import (
    CLINICIAN_NAME_LABEL,
    DEPARTMENT_LABEL,
    SCHEDULED_DAY_LABEL,
    SHIFT_SCHEDULE_LABEL,
    STUDENT_NUMBER_LABEL,
    TIME_INTERVAL_LABEL,
)
from .form_urls import FormUrlError, validate_form_url
from .models import ClinicianProfile


SAFE_PREFILL_ERROR = "Visible tabs could not be prepared. Check the form fields and try again."
DATA_PARAMS_PATTERN = re.compile(r'data-params="([^"]+)"')


class PrefillUrlError(ValueError):
    pass


def _extract_entry_ids(page_html: str) -> dict[str, int]:
    entry_ids: dict[str, int] = {}
    for encoded_params in DATA_PARAMS_PATTERN.findall(page_html):
        try:
            raw_params = html.unescape(encoded_params).removeprefix("%.@.")
            params, _ = json.JSONDecoder().raw_decode(raw_params)
            label = params[1]
            entry_id = params[4][0][0]
        except (IndexError, json.JSONDecodeError, TypeError):
            continue
        if isinstance(label, str) and isinstance(entry_id, int):
            entry_ids[label] = entry_id
    return entry_ids


def _canonical_viewform_url(value: str) -> str:
    try:
        validate_form_url(value)
    except (FormUrlError, ValueError) as error:
        raise PrefillUrlError(SAFE_PREFILL_ERROR) from error

    parsed = urlsplit(value)
    if parsed.hostname != "docs.google.com" or not parsed.path.endswith("/viewform"):
        raise PrefillUrlError(SAFE_PREFILL_ERROR)
    return urlunsplit(("https", "docs.google.com", parsed.path, "", ""))


def build_prefill_urls(
    form_url: str,
    profiles: list[ClinicianProfile],
    *,
    timeout_seconds: float = 20,
) -> list[str]:
    try:
        response = httpx.get(
            form_url,
            follow_redirects=True,
            timeout=timeout_seconds,
        )
        response.raise_for_status()
        viewform_url = _canonical_viewform_url(str(response.url))
    except (httpx.HTTPError, PrefillUrlError) as error:
        raise PrefillUrlError(SAFE_PREFILL_ERROR) from error

    entry_ids = _extract_entry_ids(response.text)
    required_labels = {
        CLINICIAN_NAME_LABEL,
        STUDENT_NUMBER_LABEL,
        SCHEDULED_DAY_LABEL,
        SHIFT_SCHEDULE_LABEL,
        DEPARTMENT_LABEL,
        TIME_INTERVAL_LABEL,
    }
    if not required_labels.issubset(entry_ids):
        raise PrefillUrlError(SAFE_PREFILL_ERROR)

    urls: list[str] = []
    for profile in profiles:
        query = urlencode(
            {
                "usp": "pp_url",
                "emailAddress": profile.email,
                f"entry.{entry_ids[CLINICIAN_NAME_LABEL]}": profile.clinician_name,
                f"entry.{entry_ids[STUDENT_NUMBER_LABEL]}": profile.student_number,
                f"entry.{entry_ids[SCHEDULED_DAY_LABEL]}": profile.scheduled_day,
                f"entry.{entry_ids[SHIFT_SCHEDULE_LABEL]}": profile.shift_schedule,
                f"entry.{entry_ids[DEPARTMENT_LABEL]}": profile.department,
                f"entry.{entry_ids[TIME_INTERVAL_LABEL]}": profile.time_interval,
            }
        )
        urls.append(f"{viewform_url}?{query}")
    return urls
