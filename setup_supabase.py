import os
import json
import requests
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Table definition
TABLE_NAME = "venmo_transactions"
TABLE_SQL = """
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
"""

def setup_supabase():
    """
    Interactive setup for Supabase configuration
    """
    print("Venmo Tracker Supabase Setup")
    print("============================")
    
    # Check for existing configuration
    if os.path.exists(".env"):
        print("Found existing .env file with configuration.")
        load_dotenv()
        
    # Get Supabase URL and API key from user input or environment variables
    supabase_url = os.getenv("SUPABASE_URL") or input("Enter your Supabase URL (from Project Settings > API): ")
    supabase_key = os.getenv("SUPABASE_KEY") or input("Enter your Supabase anon key (from Project Settings > API): ")
    
    # Save to .env file
    with open(".env", "w") as f:
        f.write(f"SUPABASE_URL={supabase_url}\n")
        f.write(f"SUPABASE_KEY={supabase_key}\n")
    
    print("\nCredentials saved to .env file.")
    
    # Test the connection by making a simple REST API call to Supabase
    print("\nTesting connection to Supabase...")
    try:
        # Test the connection by simply initializing the client
        supabase = create_client(supabase_url, supabase_key)
        print("Connection successful!")
        print(f"Connected to project URL: {supabase_url}")
        
        # Guide the user through table creation
        print("\nTo create the necessary table, follow these steps:")
        print("1. Go to your Supabase dashboard")
        print("2. Navigate to the SQL Editor")
        print("3. Paste and run the following SQL:")
        print(TABLE_SQL)
        print("\nAfter creating the table, you can run 'python venmo_api.py' to start tracking transactions.")
        
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

def test_insert():
    """
    Test inserting a sample transaction into Supabase
    """
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not supabase_url or not supabase_key:
        print("Missing Supabase credentials. Please run setup first.")
        return False
    
    print("\nTesting transaction insertion...")
    
    # Sample transaction data
    test_transaction = {
        "id": "test-transaction-123",
        "transaction_date": "2025-04-05T19:00:41",
        "note": "Test transaction",
        "amount": "$0.01",
        "type": "payment",
        "sender": "Test User",
        "receiver": "Test Recipient"
    }
    
    try:
        # Connect to Supabase
        supabase = create_client(supabase_url, supabase_key)
        
        # First try to check if the table exists
        print(f"Checking if '{TABLE_NAME}' table exists...")
        try:
            # Try to insert the test transaction
            response = supabase.table(TABLE_NAME).insert(test_transaction).execute()
            
            # Check for errors
            if hasattr(response, 'error') and response.error:
                print(f"Error inserting test transaction: {response.error}")
                if "relation" in str(response.error) and "does not exist" in str(response.error):
                    print(f"The table '{TABLE_NAME}' doesn't exist yet. Please create it first.")
                    print("Run option 1 again and follow the instructions to create the table.")
                    return False
                return False
            
            print("Test transaction inserted successfully!")
            
            # Clean up - delete the test transaction
            supabase.table(TABLE_NAME).delete().eq("id", "test-transaction-123").execute()
            print("Test transaction cleaned up.")
            
            return True
        except Exception as e:
            if "relation" in str(e) and "does not exist" in str(e):
                print(f"The table '{TABLE_NAME}' doesn't exist yet. Please create it first.")
                print("Run option 1 again and follow the instructions to create the table.")
            else:
                print(f"Error testing insertion: {e}")
            return False
    except Exception as e:
        print(f"Error connecting to Supabase: {e}")
        return False

if __name__ == "__main__":
    print("Venmo Tracker Supabase Setup")
    print("----------------------------")
    print("1. Set up Supabase configuration")
    print("2. Test database connection")
    print("3. Test transaction insertion")
    print("4. Exit")
    
    choice = input("\nEnter your choice (1-4): ")
    
    if choice == "1":
        setup_supabase()
    elif choice == "2":
        load_dotenv()
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            print("Missing Supabase credentials. Please run setup first.")
        else:
            try:
                # Simply initialize the client to test the connection
                supabase = create_client(supabase_url, supabase_key)
                print("Connection successful!")
                print(f"Connected to project URL: {supabase_url}")
            except Exception as e:
                print(f"Connection failed: {e}")
    elif choice == "3":
        test_insert()
    elif choice == "4":
        print("Exiting...")
    else:
        print("Invalid choice.") 