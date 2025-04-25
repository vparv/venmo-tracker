#!/bin/bash

# Venmo Tracker API deployment script

echo "Preparing to deploy Venmo Tracker API to Vercel..."

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null
then
    echo "Vercel CLI not found. Installing..."
    npm install -g vercel
fi

# Check for environment variables file
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file with the following variables:"
    echo "SUPABASE_URL=your_supabase_url"
    echo "SUPABASE_KEY=your_supabase_key"
    echo "API_KEY=your_api_key"
    echo "USE_MOCK_API=false (set to true for development)"
    exit 1
fi

# Load environment variables
echo "Loading environment variables from .env file..."
export $(grep -v '^#' .env | xargs)

# Create the .vercel directory if it doesn't exist
mkdir -p .vercel

# Check if already logged in
if [ ! -f .vercel/project.json ]; then
    echo "Please login to Vercel:"
    vercel login
fi

# Deploy confirmation
echo "Ready to deploy to Vercel with the following settings:"
echo "SUPABASE_URL: ${SUPABASE_URL:0:20}..."
echo "SUPABASE_KEY: ${SUPABASE_KEY:0:20}..."
echo "API_KEY: ${API_KEY:0:10}..."
echo "USE_MOCK_API: $USE_MOCK_API"

read -p "Continue with deployment? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]
then
    echo "Deployment cancelled."
    exit 1
fi

# Deploy to Vercel
echo "Deploying to Vercel..."
vercel --prod

echo "Deployment complete!"
echo "Your API is now available at the URL provided by Vercel."
echo "To test your API, run: curl -H \"x-api-key: $API_KEY\" <your-vercel-url>/api/transactions" 