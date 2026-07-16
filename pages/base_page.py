"""Base class shared by every Page Object.

A page object is *stateless*: the only thing it stores is the ``page`` handle it
needs to operate. It holds **no** test data and **no** cached element handles — only
lazy locator definitions (declared as properties on subclasses). That keeps page
objects reusable, parallel-safe under ``pytest-xdist``, and understandable in
isolation.
"""

from __future__ import annotations

from playwright.sync_api import Page


class BasePage:
    """Common foundation for all pages."""

    def __init__(self, page: Page) -> None:
        self.page = page

    def open(self, path: str = "/") -> None:
        """Navigate to ``path`` relative to the context's ``base_url``."""
        self.page.goto(path)
