import re
from playwright.sync_api import Playwright, sync_playwright, expect


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://venmo.com/")
    page.get_by_role("link", name="Log in").click()
    page.goto("https://venmo.com/")
    page.get_by_role("link", name="Log in").click()
    page.get_by_test_id("text-input-public-cred").click()
    page.get_by_test_id("text-input-public-cred").fill("5714991539")
    page.get_by_test_id("button-next").click()
    page.get_by_test_id("text-input-password").click()
    page.get_by_test_id("text-input-password").fill("Parvathala12#")
    page.get_by_test_id("button-submit").click()
    page.get_by_role("button", name="Send code").click()
    page.get_by_role("spinbutton", name="confirmation code").click()
    page.get_by_role("spinbutton", name="confirmation code").fill("988452")
    page.get_by_role("button", name="Confirm it").click()
    page.get_by_role("tab", name="mine").click()


with sync_playwright() as playwright:
    run(playwright)
