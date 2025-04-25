import json

TARGET_DOMAIN = "account.venmo.com"
TARGET_URL = "https://account.venmo.com/api/stories?feedType=me&externalId=2448403887816704462"

# Optional: add custom headers
HEADERS = {
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
    "accept": "*/*",
    "referer": "https://account.venmo.com/",
    "accept-language": "en-US,en;q=0.9"
}

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

def build_curl_command(url, headers, cookies):
    header_flags = " \\\n  ".join([f"-H '{k}: {v}'" for k, v in headers.items()])
    cookie_header = f"-H 'cookie: {format_cookies_for_header(cookies)}'"
    return f"""curl '{url}' \\
  {header_flags} \\
  {cookie_header} \\
  --compressed
"""

if __name__ == "__main__":
    all_cookies = load_cookies()
    matched_cookies = filter_cookies(all_cookies, TARGET_DOMAIN)
    curl_command = build_curl_command(TARGET_URL, HEADERS, matched_cookies)
    print("\n[✅] Generated cURL command:\n")
    print(curl_command)
