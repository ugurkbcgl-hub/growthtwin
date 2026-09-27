"""Run the profile-edit browser flow against the approved staging app."""

import getpass
import sys
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright

from e2e.profile_edit_flow import PROFILE_PATH, E2EFailure, run_profile_edit_flow

STAGING_URL = "https://growthtwin-stage-270927-9d8c14f4e775.herokuapp.com"
STAGING_HOST = "growthtwin-stage-270927-9d8c14f4e775.herokuapp.com"


def main() -> int:
    parsed = urlparse(STAGING_URL)
    if parsed.scheme != "https" or parsed.hostname != STAGING_HOST:
        print("Refusing to run against an unapproved host.", file=sys.stderr)
        return 2

    username = input("Disposable staging E2E username: ").strip()
    password = getpass.getpass("Staging E2E password (hidden): ")
    if not username or not password:
        print("A test username and password are required.", file=sys.stderr)
        return 2

    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                context = browser.new_context()
                try:
                    page = context.new_page()
                    run_profile_edit_flow(
                        page,
                        STAGING_URL,
                        username,
                        password,
                    )
                finally:
                    context.close()
            finally:
                browser.close()
    except E2EFailure as error:
        print(f"Staging E2E failed: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(
            f"Staging E2E stopped ({type(error).__name__}); sensitive details were suppressed.",
            file=sys.stderr,
        )
        return 1

    print(f"Staging E2E passed for {PROFILE_PATH}; no browser state was saved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
