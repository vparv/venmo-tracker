import requests
import json
import os
import uuid
import random
from datetime import datetime, timedelta
import supabase
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

# Add Supabase configuration from environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL")  # Found in Project Settings > API > Project URL
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Found in Project Settings > API > Project API Keys (use the anon public key)
TRANSACTIONS_TABLE = "venmo_transactions"

# Mock API settings
USE_MOCK_API = os.getenv("USE_MOCK_API", "false").lower() in ["true", "1", "yes"]

# Data directory setup
DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

# File paths
VENMO_DATA_FILE = DATA_DIR / "venmo_data.json"
MOCK_DATA_FILE = DATA_DIR / "mock_venmo_data.json"

# Initialize Supabase client
def init_supabase():
    """
    Initialize and return a Supabase client.
    """
    try:
        if not SUPABASE_URL or not SUPABASE_KEY:
            print("Supabase credentials not found. Please run setup_supabase.py first.")
            return None
            
        client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
        return None

def create_transactions_table(supabase_client):
    """
    Checks if the transactions table exists.
    Returns helpful message if it doesn't.
    """
    try:
        # Try a simple operation to check if the table exists
        supabase_client.table(TRANSACTIONS_TABLE).select("count", count="exact").limit(0).execute()
        print(f"Table '{TRANSACTIONS_TABLE}' exists.")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print(f"Table '{TRANSACTIONS_TABLE}' doesn't exist.")
            print("Please run setup_supabase.py and follow the instructions to create the table.")
            print("""
CREATE TABLE venmo_transactions (
    id TEXT PRIMARY KEY,
    transaction_date TIMESTAMP WITH TIME ZONE,
    note TEXT,
    amount TEXT,
    type TEXT,
    sender TEXT,
    receiver TEXT,
    added_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
            """)
        else:
            print(f"Error checking table: {e}")
        return False

def insert_transaction(supabase_client, transaction):
    """
    Inserts a single transaction into Supabase.
    """
    try:
        # Extract relevant data
        transaction_id = transaction.get("id")
        
        # Check if transaction already exists in Supabase
        response = supabase_client.table(TRANSACTIONS_TABLE).select("id").eq("id", transaction_id).execute()
        if hasattr(response, 'data') and response.data and len(response.data) > 0:
            print(f"Transaction {transaction_id} already exists in Supabase, skipping.")
            return True
        
        # Build simplified data structure for the database
        transaction_data = {
            "id": transaction_id,
            "transaction_date": transaction.get("date"),
            "note": transaction.get("note", {}).get("content") if isinstance(transaction.get("note"), dict) else transaction.get("note"),
            "amount": transaction.get("amount"),
            "type": transaction.get("type"),
            "sender": transaction.get("title", {}).get("sender", {}).get("username") if isinstance(transaction.get("title"), dict) else None,
            "receiver": transaction.get("title", {}).get("receiver", {}).get("displayName") if isinstance(transaction.get("title"), dict) else None
        }
        
        # Insert the data
        response = supabase_client.table(TRANSACTIONS_TABLE).insert(transaction_data).execute()
        
        if hasattr(response, 'error') and response.error:
            print(f"Error inserting transaction {transaction_id}: {response.error}")
            return False
        return True
    except Exception as e:
        print(f"Error inserting transaction: {e}")
        return False

def sync_transactions_to_supabase(transactions, supabase_client=None):
    """
    Syncs a list of transactions to Supabase.
    """
    # If no client is provided, initialize one
    if not supabase_client:
        supabase_client = init_supabase()
        if not supabase_client:
            print("Failed to initialize Supabase client.")
            return False
    
    # Check if table exists (or create it)
    if not create_transactions_table(supabase_client):
        print("Please create the table in Supabase and try again.")
        return False
    
    # Insert each transaction
    success_count = 0
    for transaction in transactions:
        if insert_transaction(supabase_client, transaction):
            success_count += 1
    
    print(f"Successfully inserted {success_count} of {len(transactions)} transactions into Supabase.")
    return success_count == len(transactions)

def generate_mock_api_response(supabase_client):
    """
    Generates a mock Venmo API response that matches the structure of the real API.
    This simulates only the API response, not the full mock data generation system.
    Pulls existing transactions from Supabase.
    """
    # Create 5-10 mock transactions if none exist in Supabase
    mock_stories = []
    
    # First try to get existing transactions from Supabase
    try:
        response = supabase_client.table(TRANSACTIONS_TABLE).select("*").order("transaction_date", desc=True).limit(15).execute()
        if hasattr(response, 'data') and response.data and len(response.data) > 0:
            # Convert Supabase transactions to the Venmo API format
            for transaction in response.data:
                mock_transaction = {
                    "id": transaction.get("id"),
                    "date": transaction.get("transaction_date"),
                    "amount": transaction.get("amount"),
                    "type": transaction.get("type"),
                    "note": {
                        "content": transaction.get("note")
                    },
                    "title": {
                        "sender": {
                            "username": "mockuser",
                            "displayName": transaction.get("sender", "Mock User")
                        },
                        "receiver": {
                            "username": "mockreciever", 
                            "displayName": transaction.get("receiver", "Mock Receiver")
                        }
                    }
                }
                mock_stories.append(mock_transaction)
            
            print(f"Found {len(mock_stories)} existing mock transactions in Supabase")
            
    except Exception as e:
        print(f"Error fetching mock transactions from Supabase: {e}")
    
    # If no transactions found, generate some initial ones
    if not mock_stories:
        print("No existing transactions found in Supabase, generating initial set")
        num_transactions = random.randint(5, 10)
        
        for i in range(num_transactions):
            # Generate a transaction that happened in the last 10 days
            days_ago = random.randint(0, 10)
            transaction_date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%dT%H:%M:%S")
            
            # Random payment or charge
            amount_type = random.choice(["+", "-"])
            amount_value = round(random.uniform(1, 100), 2)
            amount = f"{amount_type} ${amount_value}"
            
            # Simple transaction structure
            transaction = {
                "id": str(uuid.uuid4()),
                "date": transaction_date,
                "amount": amount,
                "type": "payment",
                "note": {
                    "content": f"Mock Transaction {i+1}"
                },
                "title": {
                    "sender": {
                        "username": "mockuser",
                        "displayName": "Mock User" if amount_type == "+" else "You"
                    },
                    "receiver": {
                        "username": "mockreciever",
                        "displayName": "You" if amount_type == "+" else "Mock Receiver"
                    }
                }
            }
            
            mock_stories.append(transaction)
            
            # Also insert these into Supabase
            sync_transactions_to_supabase([transaction], supabase_client)
    
    # Sort by date (newest first)
    mock_stories.sort(key=lambda x: x.get("date"), reverse=True)
    
    # Create mock API response
    mock_data = {
        "stories": mock_stories,
        "api_response_status": {
            "status_code": 200,
            "reason": "OK",
            "success": True
        }
    }
    
    return mock_data

def generate_single_mock_transaction():
    """
    Generates a single mock transaction with a timestamp newer than current time.
    """
    # Generate a transaction that happened very recently (within last hour)
    minutes_ago = random.randint(1, 60)
    transaction_date = (datetime.now() - timedelta(minutes=minutes_ago)).strftime("%Y-%m-%dT%H:%M:%S")
    
    # Random payment or charge
    amount_type = random.choice(["+", "-"])
    amount_value = round(random.uniform(1, 100), 2)
    amount = f"{amount_type} ${amount_value}"
    
    # Create more realistic transaction data
    note_options = [
        "Dinner", "Groceries", "Utilities", "Movie night", "Coffee", 
        "Gas", "Rent", "Drinks", "Concert tickets", "Lunch"
    ]
    
    # Simple transaction structure
    transaction = {
        "id": str(uuid.uuid4()),
        "date": transaction_date,
        "amount": amount,
        "type": "payment",
        "note": {
            "content": random.choice(note_options)
        },
        "title": {
            "sender": {
                "username": "mockuser",
                "displayName": "Mock User" if amount_type == "+" else "You"
            },
            "receiver": {
                "username": "mockreciever",
                "displayName": "You" if amount_type == "+" else "Mock Receiver"
            }
        }
    }
    
    return transaction

def get_venmo_data():
    """
    Makes an API request to Venmo and returns the JSON response.
    If USE_MOCK_API is True, returns a mock API response.
    Each mock API call adds a new transaction (stored in Supabase).
    """
    global USE_MOCK_API
    
    if USE_MOCK_API:
        print("Using mock Venmo API data")
        
        # Initialize Supabase client
        supabase_client = init_supabase()
        if not supabase_client:
            print("Failed to initialize Supabase client for mock data. Falling back to real API.")
            USE_MOCK_API = False
        else:
            # Check if the table exists
            if not create_transactions_table(supabase_client):
                print("Please create the table in Supabase and try again.")
                USE_MOCK_API = False
            else:
                # Get existing mock data from Supabase
                mock_data = generate_mock_api_response(supabase_client)
                
                # Always add a new transaction with each API call
                new_transaction = generate_single_mock_transaction()
                
                # Ensure this transaction has the newest date
                if mock_data["stories"]:
                    newest_transaction_date = max(
                        datetime.fromisoformat(story["date"].replace("Z", "+00:00")) 
                        if "Z" in story["date"] else datetime.fromisoformat(story["date"])
                        for story in mock_data["stories"]
                    )
                    # Make this transaction at least 1 minute newer
                    new_date = newest_transaction_date + timedelta(minutes=1)
                    new_transaction["date"] = new_date.strftime("%Y-%m-%dT%H:%M:%S")
                
                # Add the new transaction to the response
                mock_data["stories"].insert(0, new_transaction)
                print(f"Added new mock transaction: {new_transaction['note']['content']} ({new_transaction['amount']})")
                
                # Insert the new transaction into Supabase directly
                sync_transactions_to_supabase([new_transaction], supabase_client)
                
                return mock_data
    
    # If not using mock API, proceed with real API call
    headers = {
        'sec-ch-ua-platform': '"macOS"',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="134", "Not:A-Brand";v="24", "Google Chrome";v="134"',
        'sec-ch-ua-mobile': '?0',
        'accept': '*/*',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://account.venmo.com/',
        'accept-language': 'en-US,en;q=0.9',
        'cookie': 'v_id=fp01-ad4408db-e3ad-4ac7-87f6-f8c3d6c81244; enforce_policy=ccpa; login_email=; cookie_prefs=T%3D1%2CP%3D1%2CF%3D1%2Ctype%3Dexplicit_banner; d_id=022387f6b1a04b9299ae8e8fa3f6d0281743609213865; _gid=GA1.2.229760370.1743877355; s_id=18776bab-0593-450b-8d3b-7d0376a50e9a; _csrf=DIZjOLIlbgAiwgHUSBfP1a-u; tsrce=identityappsnodeweb; l7_az=dcg04.phx; ts=vreXpYrS%3D1775413358%26vteXpYrS%3D1743879158%26vr%3Df4254c681950ad1248c249cbffddca70%26vt%3D0730c1c51960accc084890fafc186649%26vtyp%3Dreturn; ts_c=vr%3Df4254c681950ad1248c249cbffddca70%26vt%3D0730c1c51960accc084890fafc186649; x-pp-s=eyJ0IjoiMTc0Mzg3NzM2MTkyOCIsImwiOiIwIiwibSI6IjAifQ; api_access_token=5f3e943942bf3ebcb234b64a2443d3047c47a6162310e0dd63b528d2036912e4; pwv_id_token=eyJraWQiOiI3MjM5YzY5YzhkMDU0YzFmOGNmYmIxMWYyODdlODcwMiIsInR5cCI6IkpXVCIsImFsZyI6IlJTMjU2In0.eyJpc3MiOiJodHRwczovL2FwaS5wYXlwYWwuY29tIiwiYXRfaGFzaCI6InJ1ZFhMZEVac3YxQXFxSTd4azNkbXciLCJzdWIiOiJodHRwczovL3d3dy5wYXlwYWwuY29tL3dlYmFwcHMvYXV0aC9pZGVudGl0eS91c2VyL1hlZDdwM1dzVlpqWVJMbmJvaWRsWmtZMGU0NFZGVFJ0RHBCYUdxRW5QZVUiLCJyb2xlIjoiQ09OU1VNRVIiLCJhbXIiOlsicGhvbmUiLCJwd2QiXSwiZXh0ZXJuYWxfaWQiOiIyNDQ4NDAzODg3ODE2NzA0NDYyIiwic2Vzc2lvbl9pbmRleCI6IlpfYWhIMXRVRUNNOXI0dEp0VHVzdDIycmtzUyIsImNsaWVudF9pZCI6IkFVd1JVYUkwMnBqNkZoWlpZYnNFMXI4d3dLeWZHbnRzQ1dqTTA3Yzc3MFdTc2FfbTdhVzhnZEw3cFNaZ25fVlFaT195aGVPMUE0cmhBTnV5IiwiYWNyIjpbInVzZXIiXSwiYXVkIjoiQVV3UlVhSTAycGo2RmhaWllic0Uxcjh3d0t5ZkdudHNDV2pNMDdjNzcwV1NzYV9tN2FXOGdkTDdwU1pnbl9WUVpPX3loZU8xQTRyaEFOdXkiLCJjX2hhc2giOiJDRXlCeHFNSkpxdzZMSlJYcmdaT1N3IiwiYXV0aF90aW1lIjoxNzQzODc3MzYxLCJvcHRpb25zIjp7fSwiYXoiOiJkY2cwNC5waHgiLCJleHAiOjE3NDM4NzgyNjEsImlhdCI6MTc0Mzg3NzM2MSwianRpIjoiVTJBQU5ITXcwRmotUXNSV3E1VF9pUGphVGcxaV84YllIQWxiOXpkS1ItWkwwZElGaE0td245dkp2dEVyNGRSeW52RDlQOUtNTTRyeUF3dUFraHF0dFpEVE1uREZsVU5fX2JrQm9CSTN3Q2p5Z2dLWEdmeGpuSWVONUNhV25qbGcifQ.HhRZbjoFAo_YFdf3zr5ikt_3297QZoMH_AIiB4Itr-SOZ8W_Am94oHSCVMlXD1r6epyufpARibnjn99eaGQgB1k6otDMefjPp8OO6Fml7Zv14R1JWdb9F8YGu1P4Ozh7ApNBALll2xLynFnRpQtcxzpDloN2mU0Z2L0Ke4d1kOZisztdJ7NrLXNAvbUzLYNhQ_4RPbE2F6Iz9cb5TOaRSsjsv5TTDi2GBMCN_RHlAsDmyuK2M0TbCm_aRM4HdKC7Y0R2EN-9rbuOPqTeVGQ7Q5cQhFZYbz5Iuovm7V5pAc3-zNqPHYnEJSbYv8-qBDBL3otx4DCzpfBDyPHdvmgC6w; w_fc=8367168f-3a56-46e6-942a-1f4cfd209b53; _ga=GA1.1.84301772.1743609220; _ga_9EEMPVZPSW=GS1.1.1743877364.4.1.1743878086.0.0.0; _dd_s=logs=0&expire=1743878986789&rum=2&id=30459b6b-3ce8-44f1-a2d7-73fd5afa7963&created=1743877364299; _ga_ZCV327BG16=GS1.1.1743877364.1.1.1743878087.0.0.0; aws-waf-token=a1fe274e-f37d-4d0e-a7c6-60f9aab812ac:EQoAg7WCK4tAAAAA:oQ5+HS4GSrBeLacrRMkooPXNyJ1i4alUmLj9E+x7JY7qw7WyD5TnRPTwhKljk3B3kKCPcIlj7PCwF39+G+kN+qIpLZHVdVhwwNYB0jKKK8y9OSlRc0NuJ1GL8516ZQjRMMtPH3LjMeI1sCOZiV9/M8O9ihXHXQsKb5p7fEALbaIzEUhbwF2cEUNnvWPNhWwxXR70ug==',
        'priority': 'u=1, i'
    }
    
    url = 'https://account.venmo.com/api/stories'
    params = {
        'feedType': 'me',
        'externalId': '2448403887816704462'
    }
    
    try:
        # Using the requests library to simulate the curl command
        response = requests.get(url, headers=headers, params=params)
        
        # Log the API response status
        status_info = {
            "status_code": response.status_code,
            "reason": response.reason,
            "success": response.ok
        }
        print(f"Venmo API Response Status: {response.status_code} {response.reason}")
        
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse and return the JSON response
        json_data = response.json()
        
        # Add the status information to the response
        json_data["api_response_status"] = status_info
        
        return json_data
    except requests.exceptions.RequestException as e:
        print(f"Error making request: {e}")
        return {
            "api_response_status": {
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                "reason": getattr(e.response, 'reason', str(e)) if hasattr(e, 'response') else str(e),
                "success": False
            },
            "stories": []
        }
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        return {
            "api_response_status": {
                "status_code": getattr(response, 'status_code', None),
                "reason": f"JSON Decode Error: {str(e)}",
                "success": False
            },
            "stories": []
        }

def save_data_to_json(data, filename=VENMO_DATA_FILE):
    """
    Save data to a JSON file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving data to {filename}: {e}")
        return False

def load_json_data(filename=VENMO_DATA_FILE):
    """
    Load data from a JSON file
    """
    try:
        if not os.path.exists(filename):
            return None
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading data from {filename}: {e}")
        return None

def get_existing_transactions(supabase_client):
    """
    Gets all existing transaction IDs from Supabase.
    """
    try:
        response = supabase_client.table(TRANSACTIONS_TABLE).select("id").execute()
        if hasattr(response, 'data') and response.data:
            return [item['id'] for item in response.data]
        return []
    except Exception as e:
        print(f"Error getting existing transactions from Supabase: {e}")
        return []

def find_new_transactions(current_data, supabase_client):
    """
    Compares current data with transactions in Supabase to find new transactions.
    Returns a list of new transactions.
    """
    # Get lists of transactions from current data
    current_stories = current_data.get('stories', [])
    
    # Get existing transaction IDs from Supabase
    existing_ids = set(get_existing_transactions(supabase_client))
    
    # Find transactions in current data that aren't in Supabase
    new_transactions = [
        story for story in current_stories 
        if 'id' in story and story['id'] not in existing_ids
    ]
    
    return new_transactions

def check_for_new_transactions():
    """
    Main function to check for new transactions:
    1. Gets current data from Venmo API
    2. Compares with transactions in Supabase to find new ones
    3. Saves new transactions to a separate file
    4. Syncs new transactions to Supabase
    """
    # Initialize Supabase client
    supabase_client = init_supabase()
    if not supabase_client:
        print("Failed to initialize Supabase client. Exiting.")
        return False
    
    # Check if table exists
    if not create_transactions_table(supabase_client):
        print("Please create the table in Supabase and try again.")
        return False
    
    # Get current data
    current_data = get_venmo_data()
    if not current_data:
        print("Failed to get current data. Exiting.")
        return False
    
    # Check API status
    api_status = current_data.get("api_response_status", {})
    print(f"API Status: {api_status.get('success', False)}")
    
    if not api_status.get("success", False):
        print(f"API call failed with status {api_status.get('status_code')} {api_status.get('reason')}")
        # Save the error information
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "api_status": api_status
        }
        save_data_to_json(error_data, "venmo_api_error.json")
        return False
    
    # Find new transactions
    new_transactions = find_new_transactions(current_data, supabase_client)
    
    # Create a helpful summary of the data
    transaction_summary = []
    for transaction in new_transactions:
        summary = {
            "id": transaction.get("id"),
            "date": transaction.get("date"),
            "note": transaction.get("note"),
            "amount": transaction.get("amount"),
            "type": transaction.get("type"),
            "title": transaction.get("title")
        }
        transaction_summary.append(summary)
    
    # Structure the new transactions data
    new_transactions_data = {
        "timestamp": datetime.now().isoformat(),
        "count": len(new_transactions),
        "transactions": new_transactions,
        "summary": transaction_summary,
        "api_status": api_status
    }
    
    # Save new transactions to file
    if new_transactions:
        print(f"Found {len(new_transactions)} new transactions!")
        for summary in transaction_summary:
            print(f"- {summary.get('date')}: {summary.get('note')} ({summary.get('amount')})")
        save_data_to_json(new_transactions_data, "new_transactions.json")
        
        # Sync new transactions to Supabase
        print("Syncing transactions to Supabase...")
        sync_transactions_to_supabase(new_transactions, supabase_client)
    else:
        print("No new transactions found.")
    
    return len(new_transactions) > 0

if __name__ == "__main__":
    # Allow command line override of mock API setting
    import sys
    if len(sys.argv) > 1 and sys.argv[1].lower() in ["--mock", "--use-mock", "--mock-api"]:
        USE_MOCK_API = True
        print("Mock API mode enabled via command line")
    
    check_for_new_transactions() 