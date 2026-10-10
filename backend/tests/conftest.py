import pytest

from backend.app.main import store


@pytest.fixture(autouse=True)
def reset_store():
    store.clear()
    yield
    store.clear()
