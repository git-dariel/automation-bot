import re
from urllib.parse import urlsplit


FORM_PATH = re.compile(r"^/forms/d/e/([^/]+)/(?:viewform|formResponse)/?$")
SHORT_FORM_PATH = re.compile(r"^/[A-Za-z0-9_-]+/?$")


class FormUrlError(ValueError):
    pass


def validate_form_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
        raise FormUrlError("Use a valid HTTPS Google Forms URL.")

    hostname = (parsed.hostname or "").lower()
    if hostname == "forms.gle":
        if not SHORT_FORM_PATH.match(parsed.path):
            raise FormUrlError("Use a valid Google Forms short URL.")
        return parsed.path.strip("/")

    if hostname == "docs.google.com":
        match = FORM_PATH.match(parsed.path)
        if not match:
            raise FormUrlError("Use a valid public Google Forms URL.")
        return match.group(1)

    raise FormUrlError("Only Google Forms URLs are supported.")
