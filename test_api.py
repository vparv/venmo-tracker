import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API settings
BASE_URL = "http://localhost:8000"
API_KEY = os.getenv("API_KEY", "default-dev-key")

def test_health_endpoint():
    """Test the health check endpoint"""
    response = requests.get(f"{BASE_URL}/api/health")
    print("\n=== Health Endpoint ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    return response.json()

def test_transactions_endpoint():
    """Test the transactions endpoint with API key"""
    headers = {"x-api-key": API_KEY}
    response = requests.get(f"{BASE_URL}/api/transactions", headers=headers)
    print("\n=== Transactions Endpoint ===")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Transaction Count: {data.get('count')}")
        print(f"New Transactions: {data.get('new_transactions')}")
        print(f"API Status: {data.get('api_status')}")
        # Print just a few transactions to avoid flooding the console
        print(f"First few transactions: {json.dumps(data.get('transactions', [])[:2], indent=2)}")
    else:
        print(f"Error: {response.text}")
    return response

def test_invalid_api_key():
    """Test the transactions endpoint with an invalid API key"""
    headers = {"x-api-key": "invalid-key"}
    response = requests.get(f"{BASE_URL}/api/transactions", headers=headers)
    print("\n=== Invalid API Key Test ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    assert response.status_code == 401
    return response

if __name__ == "__main__":
    print("Testing Venmo Tracker API...")
    
    # Test health endpoint
    test_health_endpoint()
    
    # Test transactions endpoint
    test_transactions_endpoint()
    
    # Test invalid API key
    test_invalid_api_key()
    
    print("\nTests completed!") 