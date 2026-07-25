"""A shared fixture for loading environment variables from a ``.env`` file into the process environment.
"""

from __future__ import annotations

import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(scope="session", autouse=True)
def _load_env() -> None:
    """Read ``.env`` into the environment once per run.

    ``override=False`` means a real environment variable (as set by CI) always
    wins over a value in the file.
    """
    load_dotenv(override=False)


# --- UI target: SauceDemo ---------------------------------------------------
@pytest.fixture(scope="session")
def ui_base_url(_load_env: None) -> str:
    return os.getenv("UI_BASE_URL", "https://www.saucedemo.com")


@pytest.fixture(scope="session")
def sauce_credentials(_load_env: None) -> dict[str, str]:
    return {
        "username": os.getenv("SAUCE_USERNAME", "standard_user"),
        "password": os.getenv("SAUCE_PASSWORD", "secret_sauce"),
    }


# --- API target: restful-booker ---------------------------------------------
@pytest.fixture(scope="session")
def api_base_url(_load_env: None) -> str:
    return os.getenv("API_BASE_URL", "https://restful-booker.herokuapp.com")


@pytest.fixture(scope="session")
def booker_credentials(_load_env: None) -> dict[str, str]:
    return {
        "username": os.getenv("BOOKER_USERNAME", "admin"),
        "password": os.getenv("BOOKER_PASSWORD", "password123"),
    }


# --- Other -------------------------------------------------------------------
@pytest.fixture(scope="session")
def default_timeout_ms(_load_env: None) -> int:
    return int(os.getenv("DEFAULT_TIMEOUT_MS", "15000"))
