"""Reusable browser flow for local and approved staging checks."""

from urllib.parse import parse_qs, urljoin, urlparse

from playwright.sync_api import Page

PROFILE_PATH = "/demo/profile/"
LOGIN_PATH = "/accounts/login/"


class E2EFailure(AssertionError):
    """An expected browser checkpoint was not reached."""


def run_profile_edit_flow(
    page: Page, base_url: str, username: str, password: str
) -> None:
    """Log in, save synthetic profile data, verify persistence, and log out."""
    profile_url = urljoin(base_url.rstrip("/") + "/", PROFILE_PATH.lstrip("/"))
    response = page.goto(profile_url, wait_until="domcontentloaded")
    current = urlparse(page.url)
    if (
        response is None
        or response.status >= 400
        or current.path != LOGIN_PATH
        or parse_qs(current.query).get("next") != [PROFILE_PATH]
    ):
        raise E2EFailure("Unauthenticated access did not redirect to the login page.")

    page.locator('input[name="username"]').fill(username)
    page.locator('input[name="password"]').fill(password)
    page.get_by_role("button", name="Giriş yap").click()
    page.wait_for_url(f"**{PROFILE_PATH}")
    page.get_by_role("heading", name="Demo klinik profili").wait_for()

    expected = {
        "clinic_name": "GrowthTwin E2E Sentetik Klinik",
        "city": "Test Şehri",
        "phone": "0000000000",
        "website": "https://example.invalid",
    }
    for name, value in expected.items():
        page.locator(f'input[name="{name}"]').fill(value)

    page.get_by_role("button", name="Profili kaydet").click()
    status = page.get_by_role("status")
    status.wait_for()
    if status.inner_text().strip() != "Demo klinik profili kaydedildi.":
        raise E2EFailure("The profile save confirmation was not shown.")

    page.reload(wait_until="domcontentloaded")
    for name, value in expected.items():
        if page.locator(f'input[name="{name}"]').input_value() != value:
            raise E2EFailure(
                "Saved synthetic profile data did not persist after reload."
            )

    page.get_by_role("button", name="Çıkış yap").click()
    page.wait_for_url(f"**{LOGIN_PATH}")
    page.goto(profile_url, wait_until="domcontentloaded")
    current = urlparse(page.url)
    if current.path != LOGIN_PATH or parse_qs(current.query).get("next") != [
        PROFILE_PATH
    ]:
        raise E2EFailure("A logged-out user could still open the profile page.")
