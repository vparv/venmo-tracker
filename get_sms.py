import requests
from requests.auth import HTTPBasicAuth
import urllib3
import json
import re

# Disable SSL verification warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_sms(phone_number):
    # API credentials
    username = "33ab7874f795e1f7dea774157d01a162b65a251b"
    password = ""  # No password needed as per the curl command
    
    # API endpoint
    url = f"https://api.textchest.com/sms"
    
    # Parameters
    params = {
        "number": phone_number
    }
    
    # Make the request with basic authentication and SSL verification disabled
    response = requests.get(
        url,
        params=params,
        auth=HTTPBasicAuth(username, password),
        verify=False  # Disable SSL verification
    )
    
    # Parse the JSON response
    messages = json.loads(response.text)
    
    # Get the most recent message (first in the list)
    if messages:
        latest_message = messages[0]
        print(f"\nLatest Message: {latest_message['msg']}")
        
        # Extract the verification code using regex
        code_match = re.search(r'Code: (\d+)', latest_message['msg'])
        if code_match:
            verification_code = code_match.group(1)
            print(f"Verification Code: {verification_code}")
            return verification_code
        else:
            print("No verification code found in the message")
            return None
    else:
        print("No messages found")
        return None

if __name__ == "__main__":
    # Example usage
    phone_number = "17628327690"
    get_sms(phone_number) 