# Venmo Tracker API

A lightweight API for tracking Venmo transactions and storing them in Supabase. Built with FastAPI and deployable on Vercel.

## Features

- Fetch Venmo transactions
- Compare against existing transactions in Supabase
- Add new transactions to Supabase
- Mock API support for development
- API Key authentication

## Project Structure

```
.
├── api/                # API endpoints and core functionality
├── scripts/           # Utility scripts for setup and maintenance
├── tests/            # Test files
└── templates/        # HTML templates (if needed)
```

## Local Development

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file with the following variables:
   ```
   SUPABASE_URL=your_supabase_url
   SUPABASE_KEY=your_supabase_key
   API_KEY=your_api_key
   USE_MOCK_API=true # Set to false for production
   ```
4. Run the API locally:
   ```bash
   uvicorn api.index:app --reload
   ```
5. The API will be available at `http://localhost:8000`

## API Endpoints

- `GET /`: Welcome message
- `GET /api/health`: Health check endpoint
- `GET /api/transactions`: Get transactions (requires API key)

## Deploying to Vercel

1. Install the Vercel CLI:

   ```bash
   npm i -g vercel
   ```

2. Deploy to Vercel:

   ```bash
   vercel
   ```

3. Set the environment variables in Vercel:

   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `API_KEY`
   - `USE_MOCK_API` (optional, set to "false" for production)

4. For production deployment:
   ```bash
   vercel --prod
   ```

## Using the API

Make requests to the API using the API key:

```bash
curl -H "x-api-key: your_api_key" https://your-vercel-app.vercel.app/api/transactions
```

## Development Notes

- The API uses FastAPI's dependency injection to validate the API key
- CORS is enabled for all origins
- The API returns detailed error messages for troubleshooting
- Mock API support is available for development by setting `USE_MOCK_API=true`
