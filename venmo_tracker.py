import subprocess
import json
from get_fresh_cookies import main as get_cookies
from get_curl import load_cookies, filter_cookies, format_cookies_for_header, build_curl_command

def get_venmo_data():
    print("[🔄] Starting Venmo data retrieval process...")
    
    # Step 1: Get fresh cookies
    print("\n[1️⃣] Getting fresh cookies...")
    get_cookies()
    print("[✅] Cookies retrieved successfully")
    
    # Step 2: Load and filter cookies
    print("\n[2️⃣] Loading and filtering cookies...")
    all_cookies = load_cookies()
    matched_cookies = filter_cookies(all_cookies, "account.venmo.com")
    print(f"[✅] Found {len(matched_cookies)} matching cookies")
    
    # Step 3: Build curl command
    print("\n[3️⃣] Building curl command...")
    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
        "accept": "*/*",
        "referer": "https://account.venmo.com/",
        "accept-language": "en-US,en;q=0.9"
    }
    url = "https://account.venmo.com/api/stories?feedType=me&externalId=2448403887816704462"
    curl_command = build_curl_command(url, headers, matched_cookies)
    print("[✅] Curl command generated")
    
    # Step 4: Execute curl command and get results
    print("\n[4️⃣] Executing curl command...")
    try:
        result = subprocess.run(curl_command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print("[✅] Curl command executed successfully")
            try:
                # Parse and return the JSON response
                response_data = json.loads(result.stdout)
                print("\n[🔍] API Response Structure:")
                print(json.dumps(response_data, indent=2))
                return response_data
            except json.JSONDecodeError:
                print("[❌] Failed to parse JSON response")
                return {"error": "Failed to parse JSON response"}
        else:
            print(f"[❌] Error executing curl command: {result.stderr}")
            return {"error": result.stderr}
    except Exception as e:
        print(f"[❌] Error: {str(e)}")
        return {"error": str(e)}

if __name__ == "__main__":
    result = get_venmo_data()
    print("\n[📊] Response data:")
    print(json.dumps(result, indent=2)) 