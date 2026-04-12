# Save2Gether Recommendation API

FastAPI-based recommendation engine for Save2Gether deals platform.

## Features

- 🤖 **Hybrid Recommendation Engine** - SVD collaborative filtering + content-based + popularity
- 🚀 **Fast & Async** - Built with FastAPI and async/await
- 📊 **Real-time Model Training** - Automated SVD model retraining
- 🔥 **Firebase Integration** - Direct Firestore access
- 📍 **Location-Based Filtering** - Distance-based deal recommendations
- 📚 **Interactive API Docs** - Swagger UI at `/docs`

## Quick Start

### 1. Setup Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Firebase

1. Get your Firebase service account JSON from Firebase Console
2. Save it as `backend/firebase-credentials.json`

Or set `FIREBASE_CREDENTIALS_PATH` in `.env`

### 3. Configure Environment

Update `.env` with your settings:

```env
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
```

### 4. Run the API

```bash
# Option 1: Using the startup script
bash start_api.sh

# Option 2: Direct with uvicorn
python -m uvicorn app.main:app --reload

# Option 3: Production with gunicorn
pip install gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Health & Status

- `GET /health` - Health check
- `GET /model/svd/status` - SVD model training status

### Recommendations

- `GET /recommendations/{user_id}` - Get personalized recommendations
- `POST /recommendations` - Get recommendations (POST version)
- `GET /user/{user_id}/preferences` - Get user's inferred preferences

### Deals

- `GET /deals` - Get all available deals

### Model Management

- `POST /model/svd/train` - Train/retrain SVD model

## Example Usage

### Get Recommendations

```bash
curl "http://localhost:8000/recommendations/user123?limit=10&category=Food%20%26%20Beverage"
```

Response:

```json
{
  "user_id": "user123",
  "count": 10,
  "recommendations": [
    {
      "id": "deal_456",
      "dealName": "50% Off Pizza",
      "merchantName": "Luigi's Pizzeria",
      "category": "Food & Beverage",
      "location": "123 Main St",
      "score": 0.87,
      "reason": "Trending deal"
    }
  ]
}
```

### Train SVD Model

```bash
curl -X POST http://localhost:8000/model/svd/train \
  -H "Content-Type: application/json" \
  -d '{"n_components": 20, "min_interactions": 5}'
```

### Check API Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI

## Architecture

```
┌─────────────────────┐
│   Frontend (Vue)    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│   FastAPI Server    │
│  (Recommendation    │
│   Engine)           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│    Firestore DB     │
│   (Users, Deals,    │
│   Interactions)     │
└─────────────────────┘
```

## Recommendation Algorithm

The engine uses multiple strategies:

1. **Collaborative Filtering (SVD)** - Similar users liked these deals
2. **Content-Based** - Matches your past preferences
3. **Popularity** - Trending deals right now
4. **Recency** - New deals just added
5. **Urgency** - Deals expiring soon
6. **Location** - Nearby deals

Scores are weighted and combined for final ranking.

## Deployment

### Docker

```bash
docker build -t save2gether-api .
docker run -p 8000:8000 \
  -e FIREBASE_CREDENTIALS_PATH=/app/firebase-creds.json \
  -v $(pwd)/firebase-credentials.json:/app/firebase-creds.json \
  save2gether-api
```

### Cloud Run

```bash
gcloud run deploy save2gether-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars "FIREBASE_CREDENTIALS_PATH=/app/firebase-creds.json"
```

### Railway/Heroku

1. Push to GitHub
2. Connect repository to Railway/Heroku
3. Set environment variables in dashboard
4. Deploy!

## Troubleshooting

### Import errors for numpy/sklearn

```bash
pip install --upgrade numpy scikit-learn
```

### Firebase credentials not found

- Ensure `firebase-credentials.json` is in backend directory, or
- Set `FIREBASE_CREDENTIALS_PATH` environment variable

### SVD model not training

- Check that your Firestore has users with joined deals
- Minimum 5 interactions required by default
- Check logs: `tail -f logs/api.log`

## Development

### Run tests

```bash
pytest tests/
```

### Format code

```bash
black app/
```

### Type checking

```bash
mypy app/
```

## License

MIT
