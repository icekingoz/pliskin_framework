
from playwright.sync_api import Page, expect
from pages.login_page import LoginPage, InventoryPage

def test_login_adds_item(page):
    login_page = LoginPage(page)
    login_page.open()
    inventory = login_page.login("standard_user", "secret_sauce")
    expect(inventory.title).to_have_text("Products")
    inventory.add_to_cart("Sauce Labs Backpack")
    expect(inventory.cart_badge).to_have_text("1")


def test_inventory_sorts_by_price_low_to_high(page):
    LoginPage(page).open()
    LoginPage(page).login("standard_user", "secret_sauce")

    inventory = InventoryPage(page)
    expect(inventory.inventory_items).to_have_count(6)

    inventory.sort_by("lohi")
    prices = inventory.visible_item_prices()
    assert prices == sorted(prices)