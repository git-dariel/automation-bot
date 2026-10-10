import pytest

from backend.app.form_urls import FormUrlError, validate_form_url


@pytest.mark.parametrize(
    "value",
    [
        "https://forms.gle/4Qn7MCvAzMBrR1Hw7",
        "https://forms.gle/o85CsYeaL1ujyiw56",
        "https://forms.gle/another-owned-form",
    ],
)
def test_accepts_any_well_formed_google_forms_short_url(value: str):
    assert validate_form_url(value)


def test_accepts_any_canonical_public_google_form_url():
    canonical = "https://docs.google.com/forms/d/e/another-form-id/viewform?usp=send_form"
    assert validate_form_url(canonical) == "another-form-id"


@pytest.mark.parametrize(
    "value",
    [
        "http://forms.gle/4Qn7MCvAzMBrR1Hw7",
        "https://forms.gle/",
        "https://forms.gle/valid/extra-path",
        "https://docs.google.com/forms/not-a-public-form",
        "https://example.com/forms/d/e/1/viewform",
        "https://user:pass@forms.gle/4Qn7MCvAzMBrR1Hw7",
    ],
)
def test_rejects_non_google_or_unsafe_urls(value: str):
    with pytest.raises(FormUrlError):
        validate_form_url(value)
