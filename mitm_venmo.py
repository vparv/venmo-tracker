import re
import json
from mitmproxy import http

# Domains to watch
WATCHED_DOMAINS = ["venmo.com", "paypal.com"]

# 2FA-related keywords to look for in responses
TWO_FA_KEYWORDS = [
    "2fa", "two_factor", "verify", "verification", "otp", "mfa", "code"
]

def response(flow: http.HTTPFlow) -> None:
    # Skip irrelevant domains
    if not any(domain in flow.request.host for domain in WATCHED_DOMAINS):
        return

    print(f"\n👀 [VENMO/PAYPAL] {flow.request.method} {flow.request.url}")

    # Check response content
    if flow.response and flow.response.content:
        try:
            response_text = flow.response.text.lower()

            if any(keyword in response_text for keyword in TWO_FA_KEYWORDS):
                print("🔐 2FA-related content detected!")

                try:
                    json_data = json.loads(flow.response.text)
                    print("\n📦 JSON Response:")
                    print(json.dumps(json_data, indent=2))
                except json.JSONDecodeError:
                    print("Response is not valid JSON")

        except UnicodeDecodeError:
            # Skip non-decodable responses
            pass
