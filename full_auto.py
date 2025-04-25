import json
import subprocess
import time
from playwright.sync_api import sync_playwright

# --- CONFIG --- #
MITMPROXY_PORT = 8080
LOGIN_URL = "https://account.venmo.com"
TARGET_DOMAIN = "account.venmo.com"
TARGET_URL = "https://account.venmo.com/api/stories?feedType=me&externalId=2448403887816704462"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "accept": "*/*",
    "referer": "https://account.venmo.com/",
    "accept-language": "en-US,en;q=0.9"
}
# -------------- #

def start_mitmproxy():
    print("🚀 Starting mitmdump...")
    subprocess.Popen(["mitmdump", "-w", "flows.mitm"])
    time.sleep(2)  # Give it time to start

def login_with_browser():
    print("🧑‍💻 Opening browser for manual login (2FA)...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, proxy={"server": f"http://localhost:{MITMPROXY_PORT}"})
        context = browser.new_context()
        page = context.new_page()
        page.goto(LOGIN_URL)

        input("⏸  After logging in and completing 2FA, press Enter to continue...")

        cookies = context.cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)

        print(f"✅ Saved {len(cookies)} cookies to cookies.json")
        browser.close()

def load_cookies(path="cookies.json"):
    with open(path, "r") as f:
        return json.load(f)

def filter_cookies(cookies, domain):
    return [
        c for c in cookies
        if domain.endswith(c["domain"].lstrip(".")) or c["domain"].lstrip(".").endswith(domain)
    ]

def format_cookies_for_header(cookies):
    return "; ".join(f"{c['name']}={c['value']}" for c in cookies)

def build_and_run_curl(url, headers, cookies):
    print("🔧 Building curl command...")
    header_flags = [f"-H '{k}: {v}'" for k, v in headers.items()]
    cookie_header = f"-H 'cookie: {format_cookies_for_header(cookies)}'"
    curl_command = ["curl", url, "--compressed"] + header_flags + [cookie_header]

    print("📡 Running curl...\n")
    subprocess.run(" ".join(curl_command), shell=True)

if __name__ == "__main__":
    start_mitmproxy()
    login_with_browser()
    cookies = filter_cookies(load_cookies(), TARGET_DOMAIN)
    build_and_run_curl(TARGET_URL, HEADERS, cookies)
