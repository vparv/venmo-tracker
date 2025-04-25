from fastapi import FastAPI, HTTPException, Depends, Security, status
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import json
from datetime import datetime

# Import functions from venmo_api.py
from .venmo_api import (
    get_venmo_data, 
    init_supabase, 
    create_transactions_table,
    find_new_transactions, 
    sync_transactions_to_supabase
)

app = FastAPI(title="Venmo Tracker API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Set up API key authentication
API_KEY = os.environ.get("API_KEY", "default-dev-key")
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)

def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key"
    )

# Response models
class Transaction(BaseModel):
    id: str
    transaction_date: Optional[str] = None
    note: Optional[str] = None
    amount: Optional[str] = None
    type: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None

class TransactionResponse(BaseModel):
    count: int
    new_transactions: int
    transactions: List[Dict[str, Any]]
    api_status: Dict[str, Any]
    mock_mode: bool
    timestamp: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the Venmo Tracker API"}

@app.get("/api/public")
def public_endpoint():
    """
    Public endpoint that doesn't require authentication
    """
    return {
        "status": "public endpoint working",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/transactions", response_model=TransactionResponse)
def get_transactions(api_key: str = Depends(get_api_key)):
    """
    Get all transactions from Venmo, and sync new ones to Supabase
    """
    try:
        # Check if mock mode is enabled
        use_mock = os.environ.get("USE_MOCK_API", "false").lower() in ["true", "1", "yes"]
        if use_mock:
            print("MOCK MODE ACTIVE: Using simulated Venmo transaction data")
        else:
            print("LIVE MODE: Using real Venmo API")
        
        # Initialize Supabase client
        supabase_client = init_supabase()
        if not supabase_client:
            print("Error: Failed to initialize Supabase client")
            raise HTTPException(status_code=500, detail="Failed to initialize Supabase client")
        
        # Check if table exists
        if not create_transactions_table(supabase_client):
            print("Error: Transactions table doesn't exist in Supabase")
            raise HTTPException(status_code=500, detail="Transactions table doesn't exist in Supabase")
        
        # Get current data from Venmo
        print("Fetching data from Venmo API...")
        current_data = get_venmo_data()
        if not current_data:
            print("Error: Failed to get data from Venmo API")
            raise HTTPException(status_code=500, detail="Failed to get data from Venmo API")
        
        # Check API status
        api_status = current_data.get("api_response_status", {})
        print(f"API Status: {api_status}")
        if not api_status.get("success", False):
            error_msg = f"Venmo API call failed: {api_status.get('status_code')} {api_status.get('reason')}"
            print(f"Error: {error_msg}")
            raise HTTPException(status_code=502, detail=error_msg)
        
        # Find new transactions
        print("Finding new transactions...")
        new_transactions = find_new_transactions(current_data, supabase_client)
        print(f"Found {len(new_transactions)} new transactions")
        
        # Sync new transactions to Supabase
        if new_transactions:
            print("Syncing new transactions to Supabase...")
            sync_result = sync_transactions_to_supabase(new_transactions, supabase_client)
            print(f"Sync result: {sync_result}")
        
        # Structure response
        stories = current_data.get("stories", [])
        print(f"Total transactions: {len(stories)}")
        response = {
            "count": len(stories),
            "new_transactions": len(new_transactions),
            "transactions": stories,
            "api_status": api_status,
            "mock_mode": use_mock,
            "timestamp": datetime.now().isoformat()
        }
        
        return response
    except Exception as e:
        print(f"Unexpected error in get_transactions: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/api/health")
def health_check():
    """
    Simple health check endpoint
    """
    use_mock = os.environ.get("USE_MOCK_API", "false").lower() in ["true", "1", "yes"]
    return {
        "status": "healthy",
        "mock_mode": use_mock,
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/db-transactions")
def get_db_transactions(api_key: str = Depends(get_api_key)):
    """
    Get all transactions directly from Supabase
    """
    try:
        # Initialize Supabase client
        supabase_client = init_supabase()
        if not supabase_client:
            print("Error: Failed to initialize Supabase client")
            raise HTTPException(status_code=500, detail="Failed to initialize Supabase client")
        
        # Check if table exists
        if not create_transactions_table(supabase_client):
            print("Error: Transactions table doesn't exist in Supabase")
            raise HTTPException(status_code=500, detail="Transactions table doesn't exist in Supabase")
        
        # Fetch all transactions from Supabase
        print("Fetching transactions from Supabase...")
        try:
            response = supabase_client.table("venmo_transactions").select("*").order("transaction_date", desc=True).execute()
            transactions = response.data if hasattr(response, 'data') else []
            print(f"Found {len(transactions)} transactions in the database")
        except Exception as db_error:
            print(f"Error fetching from Supabase: {str(db_error)}")
            raise HTTPException(status_code=500, detail=f"Database error: {str(db_error)}")
        
        return {
            "count": len(transactions),
            "transactions": transactions,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        print(f"Unexpected error in get_db_transactions: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@app.get("/api/diagnostic")
def diagnostic():
    """
    Diagnostic endpoint to check environment and configuration
    """
    try:
        # Collect environment variables (hiding sensitive parts)
        env_vars = {
            "SUPABASE_URL": os.environ.get("SUPABASE_URL", "Not set")[:15] + "..." if os.environ.get("SUPABASE_URL") else "Not set",
            "SUPABASE_KEY": "***" if os.environ.get("SUPABASE_KEY") else "Not set",
            "API_KEY": "***" if os.environ.get("API_KEY") else "Not set",
            "USE_MOCK_API": os.environ.get("USE_MOCK_API", "Not set"),
            "PYTHONPATH": os.environ.get("PYTHONPATH", "Not set"),
            "VERCEL_ENV": os.environ.get("VERCEL_ENV", "Not set"),
            "VERCEL_REGION": os.environ.get("VERCEL_REGION", "Not set")
        }
        
        # Check directory structure
        try:
            current_dir = os.getcwd()
            dir_contents = os.listdir(current_dir)
            api_dir_exists = "api" in dir_contents
            api_contents = os.listdir(os.path.join(current_dir, "api")) if api_dir_exists else []
        except Exception as dir_error:
            dir_contents = f"Error: {str(dir_error)}"
            api_dir_exists = "Unknown"
            api_contents = "Unknown"
        
        # Try to initialize Supabase (without full operations)
        supabase_init_success = False
        supabase_error = None
        try:
            from .venmo_api import init_supabase
            client = init_supabase()
            supabase_init_success = client is not None
        except Exception as e:
            supabase_error = str(e)
        
        # Return diagnostic information
        return {
            "timestamp": datetime.now().isoformat(),
            "environment_variables": env_vars,
            "directory_structure": {
                "current_directory": current_dir,
                "contents": dir_contents[:20],  # Limit to first 20 items
                "api_dir_exists": api_dir_exists,
                "api_contents": api_contents
            },
            "supabase_connection": {
                "init_success": supabase_init_success,
                "error": supabase_error
            },
            "python_version": os.popen("python --version").read().strip(),
            "packages": os.popen("pip freeze").read().strip().split("\n")[:30]  # Limit to first 30 packages
        }
    except Exception as e:
        return {
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# This is needed for Vercel serverless deployment
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 