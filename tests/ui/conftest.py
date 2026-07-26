"""Fixtures for the UI suite only."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.login_page import LoginPage
from support.reporting import attach_html, attach_png, attach_text


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


# --- failure capture --------------------------------------------------------
@pytest.hookimpl(wrapper=True)
def pytest_runtest_makereport(item: pytest.Item, call: pytest.CallInfo):
    """Attach a screenshot, the URL and the DOM whenever a UI test fails.

    Playwright --screenshot=only-on-failure already writes a PNG to
    test-results folder. This hook exists because the file lives in a downloadble zip, and nobody has time for that.
    """
    report = yield

    # `call` runs three times per test (setup/call/teardown); only act on the
    # phase that actually failed, or you attach the same screenshot three times.
    if report.when != "call" or not report.failed:
        return report

    page: Page | None = item.funcargs.get("page")
    if page is None:  # not a browser test -- nothing to capture
        return report

    try:
        attach_png(
            f"screenshot-{item.name}",
            page.screenshot(full_page=True),
            item=item,
            report=report,
        )
        attach_text("page-url", page.url, item=item, report=report)
        attach_html("page-source", page.content(), item=item, report=report)
    except Exception as exc:  # pragma: no cover
        # The page can already be closed if the failure was a crash or timeout
        # during teardown. Record why capture failed rather than masking the
        # real test failure with a second, unrelated error.
        attach_text("capture-error", f"{type(exc).__name__}: {exc}", item=item, report=report)

    return report
