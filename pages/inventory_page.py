"""Page Object for the SauceDemo inventory (products) screen."""

from __future__ import annotations

from playwright.sync_api import Locator

from pages.base_page import BasePage


class InventoryPage(BasePage):
    """Product grid shown after login (``/inventory.html``)."""

    PATH = "/inventory.html"

    # -- locators ------------------------------------------------------------
    @property
    def title(self) -> Locator:
        return self.page.locator('[data-test="title"]')  # "Products"

    @property
    def inventory_items(self) -> Locator:
        return self.page.locator('[data-test="inventory-item"]')

    @property
    def item_names(self) -> Locator:
        return self.page.locator('[data-test="inventory-item-name"]')

    @property
    def item_prices(self) -> Locator:
        return self.page.locator('[data-test="inventory-item-price"]')

    @property
    def sort_dropdown(self) -> Locator:
        return self.page.locator('[data-test="product-sort-container"]')

    @property
    def cart_link(self) -> Locator:
        return self.page.locator('[data-test="shopping-cart-link"]')

    @property
    def cart_badge(self) -> Locator:
        """Counter on the cart icon; absent when the cart is empty."""
        return self.page.locator('[data-test="shopping-cart-badge"]')

    def item_by_name(self, name: str) -> Locator:
        """One product card, scoped by its visible name."""
        return self.inventory_items.filter(
            has=self.page.get_by_text(name, exact=True)
        )

    # -- actions -------------------------------------------------------------
    def open(self) -> None:
        """Direct navigation — needs an authenticated session (storage state)."""
        super().open(self.PATH)

    def add_to_cart(self, name: str) -> None:
        self.item_by_name(name).get_by_role("button", name="Add to cart").click()

    def remove_from_cart(self, name: str) -> None:
        self.item_by_name(name).get_by_role("button", name="Remove").click()

    def sort_by(self, option: str) -> None:
        """``option`` is the <select> value: az | za | lohi | hilo."""
        self.sort_dropdown.select_option(option)

    def open_cart(self) -> None:
        self.cart_link.click()

    def visible_item_names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def visible_item_prices(self) -> list[float]:
        return [float(p.removeprefix("$")) for p in self.item_prices.all_inner_texts()]