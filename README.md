# Venmo Transaction Tracker

A Flask web application that demonstrates reverse engineering the Venmo API, including automated handling of 2FA authentication flows and transaction data retrieval. The project shows how to programmatically bypass Venmo's security measures, intercept API requests, and extract transaction data through automated browser interactions and cookie manipulation.

This is a WIP! It was not meant for production use or for others to use.

## Features

- 🔐 Automated Venmo authentication with 2FA support
- 📱 SMS verification code handling
- 💰 Real-time Venmo transaction fetching
- 🌐 Clean web interface to view transactions
- 🔄 Automatic cookie management for persistent sessions
- 📊 Transaction formatting and display
- 🛡️ Error handling and debugging support

## Project Structure

```
.
├── app.py                  # Main Flask application
├── venmo_tracker.py        # Core Venmo transaction fetching logic
├── venmo_api.py           # Venmo API interaction utilities
├── login_flow.py          # Authentication flow handling
├── get_sms.py            # SMS verification code retrieval
├── send_sms.py           # SMS sending utilities
├── get_fresh_cookies.py   # Cookie management
├── setup_supabase.py     # Supabase setup and configuration
├── templates/            # Flask HTML templates
├── requirements.txt      # Python dependencies
└── .env                 # Environment configuration
```

## Prerequisites

- Python 3.8 or higher
- A Venmo account
- A phone number for 2FA verification through TextChest
- (Optional) Supabase account for data storage

## Installation

1. Clone the repository:

   ```bash
   git clone <repository-url>
   cd venmo-tracker
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with the following variables:
   ```
   VENMO_USERNAME=your_venmo_email
   VENMO_PASSWORD=your_venmo_password
   PHONE_NUMBER=your_2fa_phone_number
   SUPABASE_URL=your_supabase_url         # Optional
   SUPABASE_KEY=your_supabase_key         # Optional
   ```

## Running the Application

1. Start the MITM Proxy
   mitmproxy -p 8080

   -> there is set up needed here but this is generally available online and not specific to the repo

   Make sure to change your WiFI proxy settings to go through this port (both HTTP and HTTPS)

   Once you're able to access the internet through a browser and traffic is showing in the MITM console, go ahead with the next step.

1) Start the Flask server:

   ```bash
   python app.py
   ```

   Open the localhost site & it will start a Playwright automation of logging in, starting 2FA verification, cookie retrieval. Once logged in, navigate to the console and click enter. It will then call Venmo's internal APIs using those cookies to retrive transactions and display them in the app.

## Authentication Flow

The application handles Venmo authentication automatically through several steps:

1. Initial login attempt with credentials
2. 2FA code reception via SMS (using TextChest as API)
3. Automatic verification code submission
4. Cookie management for session persistence

## Development

### Key Components

- `app.py`: Flask routes and transaction display logic
- `venmo_tracker.py`: Core transaction fetching functionality
- `get_fresh_cookies.py`: Cookie retrieval
- `get_sms.py`: SMS verification code retrieval
- `venmo_api.py`: Venmo API interaction utilities
-
