"""Fixtures for the UI suite only."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage


@pytest.fixture(scope="session")
def base_url(request: pytest.FixtureRequest, ui_base_url: str) -> str:
    """Override pytest-base-url's fixture so ``pytest`` works with no flags.

    An explicit ``--base-url`` still wins, so the CI invocation is unaffected.
    Without this, ``page.goto("/")`` inside the page objects fails locally.
    """
    return request.config.getoption("--base-url") or ui_base_url


@pytest.fixture(autouse=True)
def _apply_default_timeout(page: Page, default_timeout_ms: int) -> None:
    """Make DEFAULT_TIMEOUT_MS from .env actually mean something."""
    page.set_default_timeout(default_timeout_ms)


@pytest.fixture
def logged_in_page(page: Page, sauce_credentials: dict[str, str]) -> Page:
    """A page already past the login screen, sitting on the inventory.

    Lets a test that is really about sorting or the cart skip re-testing login.
    """
    login_page = LoginPage(page)
    login_page.open()
    login_page.login(**sauce_credentials)
    return page
