from __future__ import annotations

from playwright.sync_api import Locator

from pages.base_page import BasePage
from pages.inventory_page import InventoryPage


class LoginPage(BasePage):
    """Entry point of the app (``/``)."""

    PATH = "/"

    # -- locators (lazy, resolved on use) ------------------------------------
    @property
    def username_input(self) -> Locator:
        return self.page.locator('[data-test="username"]')

    @property
    def password_input(self) -> Locator:
        return self.page.locator('[data-test="password"]')

    @property
    def login_button(self) -> Locator:
        return self.page.locator('[data-test="login-button"]')

    @property
    def error_message(self) -> Locator:
        """Red banner on failed login — assert on it from the test."""
        return self.page.locator('[data-test="error"]')

    # -- actions -------------------------------------------------------------
    def open(self) -> None:
        super().open(self.PATH)

    def login(self, username: str, password: str) -> InventoryPage:
        """Happy path; returns the page object the user lands on."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()
        return InventoryPage(self.page)

    def login_expecting_failure(self, username: str, password: str) -> None:
        """Same steps, no navigation; test asserts on ``error_message``."""
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.login_button.click()