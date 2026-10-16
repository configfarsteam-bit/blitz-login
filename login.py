"""Blitz.cloud daily login — powered by ConfigFars™"""
import os
import sys
from urllib.parse import urlparse

from playwright.sync_api import (
    Error as PWError,
    TimeoutError as PWTimeout,
    sync_playwright,
)

START_URL = "https://dashboard.blitz.cloud/"
NAV_TIMEOUT = 45_000
UI_TIMEOUT = 15_000

CONFIRMED, FAILED, UNCONFIRMED = "LOGIN_CONFIRMED", "LOGIN_FAILED", "LOGIN_UNCONFIRMED"
EXIT = {CONFIRMED: 0, FAILED: 1, UNCONFIRMED: 2}

CHALLENGE_WORDS = ("captcha", "verify you are human", "two-factor", "2fa",
                   "verification code", "authenticator", "security check")
ERROR_WORDS = ("invalid", "incorrect", "wrong", "failed", "not found", "try again")


def finish(status: str, detail: str = "") -> None:
    print(f"RESULT: {status}" + (f" — {detail}" if detail else ""), flush=True)
    sys.exit(EXIT[status])


def main() -> None:
    email, password = os.environ.get("EMAIL"), os.environ.get("PAS")
    missing = [n for n, v in (("EMAIL", email), ("PAS", password)) if not v]
    if missing:
        print(f"ERROR: missing secret(s): {', '.join(missing)}", file=sys.stderr)
        sys.exit(3)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        try:
            page = browser.new_context().new_page()
            page.set_default_timeout(UI_TIMEOUT)

            # Step 1: open dashboard (follows redirects to login.blitz.cloud)
            try:
                page.goto(START_URL, wait_until="load", timeout=NAV_TIMEOUT)
            except (PWTimeout, PWError) as e:
                finish(UNCONFIRMED, f"navigation error: {type(e).__name__}")
            try:
                page.wait_for_load_state("networkidle", timeout=10_000)
            except PWTimeout:
                pass
            page.wait_for_timeout(2000)
            print(f"Landed on host: {urlparse(page.url).netloc}")

            email_box = page.get_by_label("Email address")
            pass_box = page.get_by_label("Password", exact=True)
            try:
                email_box.wait_for(state="visible")
                pass_box.wait_for(state="visible")
            except PWTimeout:
                finish(UNCONFIRMED, "login form not found (maybe already signed in or page changed)")

            # Step 2: fill form
            email_box.fill(email)
            pass_box.fill(password)
            if email_box.input_value() != email or not pass_box.input_value():
                finish(FAILED, "form fields were not filled")
            page.wait_for_timeout(1000)

            # Step 3: single click on Sign in
            btn = page.get_by_role("button", name="Sign in", exact=True)
            try:
                btn.wait_for(state="visible")
            except PWTimeout:
                finish(UNCONFIRMED, "Sign in button not found")
            if not btn.is_enabled():
                finish(UNCONFIRMED, "Sign in button disabled")
            btn.click()
            page.wait_for_timeout(7000)

            # Step 4: evaluate
            host = urlparse(page.url).netloc
            try:
                body = page.inner_text("body").lower()
            except PWError:
                body = ""
            form_visible = page.get_by_label("Password", exact=True).is_visible()
            print(f"Post-click host: {host}; login form visible: {form_visible}")

            if any(w in body for w in CHALLENGE_WORDS):
                finish(UNCONFIRMED, "CAPTCHA / 2FA / security check detected; not bypassed")
            if form_visible:
                if any(w in body for w in ERROR_WORDS):
                    finish(FAILED, "login form still shown with an error message")
                finish(FAILED, "login form still shown after submit")
            if host.startswith("login."):
                finish(UNCONFIRMED, "still on auth domain without form")
            if host.endswith("blitz.cloud"):
                finish(CONFIRMED, f"landed on {host} with no login form")
            finish(UNCONFIRMED, "unexpected host")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
