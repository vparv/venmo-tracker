import re
import json
from mitmproxy import http

# Replace this with the address you want to search for
SEARCH_ADDRESS = "Marisa"

def response(flow: http.HTTPFlow) -> None:
    """
    Checks the response body for the given address and adds a custom header if found.
    """
    if flow.response and flow.response.content:
        try:
            # Decode response content as text
            if re.findall(re.escape(SEARCH_ADDRESS), flow.response.text, re.IGNORECASE):
                print(f"\nMatch found in URL: {flow.request.url}")
                try:
                    # Parse and print the JSON response
                    json_data = json.loads(flow.response.text)
                    print("\nJSON Response:")
                    print(json.dumps(json_data, indent=2))
                except json.JSONDecodeError:
                    print("Response is not valid JSON")
        except UnicodeDecodeError:
            # Ignore binary/non-text responses
            pass

# Navigate to the directory this file is in and run `mitmweb -s play.py`
# Then, find the output in the terminal that starts with "HELLLLLLLOOOOOO"
# Then, copy that flow.request.url and search for it on mitmweb.
# Then, find the "Response" tab, confirm it has the desired text in it.
# Then, click "Export" and export the cURL. Place in Postman.