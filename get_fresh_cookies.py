from playwright.sync_api import sync_playwright
import json
from get_sms import get_sms
import time

MITMPROXY_PORT = 8080
TARGET_URL = "https://venmo.com/"

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            proxy={"server": f"http://localhost:{MITMPROXY_PORT}"}
        )
        context = browser.new_context()
        page = context.new_page()

        print(f"[👤] Starting automated login process...")
        
        # Navigate and enter phone number
        page.goto(TARGET_URL)
        page.get_by_role("link", name="Log in").click()
        time.sleep(3)
        page.get_by_test_id("text-input-public-cred").click()
        page.get_by_test_id("text-input-public-cred").fill("7628327690")
        time.sleep(3)
        page.get_by_test_id("button-next").click()
        time.sleep(3)
        # Enter password
        page.get_by_test_id("text-input-password").click()
        page.get_by_test_id("text-input-password").fill("Parvathala12#")
        time.sleep(3)
        page.get_by_test_id("button-submit").click()
        time.sleep(3)
        
        # Wait for and click send code button
        print("[⏳] Waiting for Send code button...")
        # Try multiple selectors for the send code button
        try:
            # First try with role and name
            time.sleep(10)
            send_code_button = page.get_by_role("button", name="Send code")
            send_code_button.wait_for(timeout=10000)
            print("[✅] Found Send code button by role and name")
            
            # Verify button is visible and enabled
            is_visible = send_code_button.is_visible()
            is_enabled = send_code_button.is_enabled()
            print(f"[🔍] Button visible: {is_visible}, enabled: {is_enabled}")
            
            # Try clicking with force option
            send_code_button.click(force=True)
            print("[✅] Clicked Send code button with force")
        except Exception as e:
            print(f"[❌] Error with first selector: {str(e)}")
            try:
                # Try alternative selector
                send_code_button = page.locator("button:has-text('Send code')")
                send_code_button.wait_for(timeout=5000)
                print("[✅] Found Send code button by text")
                send_code_button.click(force=True)
                print("[✅] Clicked Send code button with alternative selector")
            except Exception as e:
                print(f"[❌] Error with alternative selector: {str(e)}")
                print("[⚠️] Please manually click the Send code button")
                input("[⏸] Press Enter after manually clicking Send code button...")
        
        # Wait 3 seconds for the SMS to be sent
        print("[⏳] Waiting for SMS to be sent...")
        time.sleep(3)
        
        # Get verification code
        print("[📱] Retrieving verification code...")
        verification_code = get_sms("17628327690")
        if not verification_code:
            print("[❌] Failed to get verification code")
            input("[⏸] Please enter the verification code manually and press Enter to continue...")
            verification_code = input("Enter verification code: ")
        
        print(f"[🔑] Using verification code: {verification_code}")
        
        # Enter verification code
        code_input = page.get_by_role("spinbutton", name="confirmation code")
        code_input.wait_for(timeout=10000)
        code_input.fill(verification_code)
        time.sleep(3)

        page.get_by_role("button", name="Confirm it").click()
        
        # Wait for user to complete any additional steps
        input("[⏸] When you're done with any additional steps, press Enter to continue...")

        cookies = context.cookies()
        with open("cookies.json", "w") as f:
            json.dump(cookies, f, indent=2)

        print(f"[✅] Saved {len(cookies)} cookies to cookies.json")
        browser.close()

if __name__ == "__main__":
    main()
