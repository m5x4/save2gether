#!/bin/bash
# Start the Save2Gether Recommendation API

cd "$(dirname "$0")"

if [ -f .venv/bin/activate ]; then
    . .venv/bin/activate
fi

echo "Starting Save2Gether Recommendation API..."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env 2>/dev/null || echo "Please create a .env file with Firebase credentials"
fi

# Check if Firebase credentials exist
if [ ! -f firebase-credentials.json ]; then
    echo "⚠️  firebase-credentials.json not found in backend directory"
    echo "Please add your Firebase service account JSON file as firebase-credentials.json"
    exit 1
fi

# Install/upgrade dependencies
echo "Checking dependencies..."
python -m pip install -r requirements.txt -q || {
    echo "❌ Failed to install dependencies"
    exit 1
}

# Run the API
echo ""
echo "✅ Starting API server at http://localhost:8000"
echo "📚 API Docs available at http://localhost:8000/docs"
echo ""

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
