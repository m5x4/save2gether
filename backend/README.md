# Save2Gether Recommendation API

FastAPI-based recommendation engine for suggesting personalized deals to users.

## Features

### Recommendation Strategies

The engine uses a hybrid approach combining multiple strategies:

0. **SVD Collaborative Filtering**: Learns latent user-deal preferences from historical joins
1. **Content-Based Filtering**: Recommends deals based on user's past category preferences
2. **Popularity-Based**: Recommends trending deals with high click counts
3. **Recency-Based**: Prioritizes newly created deals
4. **Urgency-Based**: Highlights deals that are expiring soon
5. **Location-Based**: (Optional) Recommends nearby deals based on user location

### Scoring Algorithm

Each deal receives a composite score based on weighted components:

- SVD collaborative score: 35% (when trained and user/deal known)
- Content similarity: 25%
- Popularity: 15%
- Recency: 10%
- Urgency: 10%
- Location: 5% (when location data available)

Weights are normalized dynamically when a component is unavailable.

## Setup

### Prerequisites

- Python 3.9+
- Firebase Admin SDK credentials
- Access to Firebase Firestore database

### Installation

1. Install dependencies:

```bash
cd backend
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your Firebase credentials path:

```
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-credentials.json
API_HOST=0.0.0.0
API_PORT=8000
```

3. Run the API:

```bash
# Development
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production
python -m app.main
```

## API Endpoints

### GET /recommendations/{user_id}

Get personalized recommendations for a user.

**Parameters:**

- `user_id` (path): User's Firebase ID
- `limit` (query, optional): Number of recommendations (default: 10)
- `category` (query, optional): Filter by category
- `max_distance` (query, optional): Maximum distance in km
- `user_lat` (query, optional): User's latitude
- `user_lng` (query, optional): User's longitude

**Example:**

```bash
curl "http://localhost:8000/recommendations/user123?limit=5&category=Food%20%26%20Beverage"
```

**Response:**

```json
{
  "user_id": "user123",
  "count": 5,
  "recommendations": [
    {
      "id": "deal456",
      "dealName": "50% Off Pizza",
      "merchantName": "Pizza Palace",
      "category": "Food & Beverage",
      "location": "123 Main St, Singapore 123456",
      "score": 0.876,
      "reason": "Matches your interests"
    }
  ]
}
```

### POST /recommendations

Get recommendations with complex filtering (POST version).

**Request Body:**

```json
{
  "user_id": "user123",
  "limit": 10,
  "category": "Food & Beverage",
  "max_distance": 5.0,
  "user_lat": 1.3521,
  "user_lng": 103.8198
}
```

### GET /deals

Get all available deals.

**Parameters:**

- `category` (query, optional): Filter by category
- `limit` (query, optional): Maximum number of deals (default: 50)

### GET /user/{user_id}/preferences

Get user's inferred preferences.

**Response:**

```json
{
  "user_id": "user123",
  "preferences": {
    "categories": {
      "Food & Beverage": 45.5,
      "Retail": 30.0,
      "Travel & Attractions": 24.5
    },
    "total_deals": 11,
    "favorite_category": "Food & Beverage",
    "category_counts": {
      "Food & Beverage": 5,
      "Retail": 3,
      "Travel & Attractions": 3
    }
  }
}
```

### GET /health

Health check endpoint.

### GET /model/svd/status

Get SVD model readiness and metadata.

**Example:**

```bash
curl "http://localhost:8000/model/svd/status"
```

### POST /model/svd/train

Train/retrain the SVD model from user-deal interactions.

**Request Body:**

```json
{
  "n_components": 20,
  "min_interactions": 5
}
```

**Example:**

```bash
curl -X POST "http://localhost:8000/model/svd/train" \
  -H "Content-Type: application/json" \
  -d '{"n_components": 20, "min_interactions": 5}'
```

### Typical SVD Testing Flow (Without Frontend Integration)

```bash
# 1) Start API
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2) Train SVD model
curl -X POST "http://localhost:8000/model/svd/train" \
  -H "Content-Type: application/json" \
  -d '{"n_components": 20, "min_interactions": 5}'

# 3) Validate status
curl "http://localhost:8000/model/svd/status"

# 4) Get recommendations using hybrid + SVD
curl "http://localhost:8000/recommendations/user123?limit=10"
```

## Generate Simulated Training Data

Use the generator script to create synthetic users, deals, and interactions for offline SVD experiments.

```bash
cd backend
python scripts/generate_simulated_training_data.py \
  --num-users 250 \
  --num-deals 400 \
  --min-interactions 3 \
  --max-interactions 25 \
  --cold-start-ratio 0.2 \
  --seed 42 \
  --output-dir generated_data
```

Generated files:

- `generated_data/simulated_training_dataset.json` (all data + metadata)
- `generated_data/users.json`
- `generated_data/deals.json`
- `generated_data/interactions.csv`

Notes:

- Users are generated with `deals` as deal ID strings so they can be loaded into mock/local data services.
- The recommendation engine now supports both Firestore references and plain string IDs in `user.deals`.

## Run Local End-to-End SVD Demo

Run SVD training and recommendation generation fully offline using generated JSON files.

```bash
cd backend

# 1) Generate data
python3 scripts/generate_simulated_training_data.py --output-dir generated_data

# 2) Train + recommend (in-memory, no Firebase)
python3 scripts/run_svd_demo.py \
  --data-dir generated_data \
  --limit 10 \
  --n-components 20 \
  --min-interactions 5
```

Optional:

```bash
python3 scripts/run_svd_demo.py --data-dir generated_data --user-id user_00001 --category Retail
```

## Integration with Vue Frontend

### Using Axios

```javascript
import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

// Get recommendations
async function getRecommendations(userId, limit = 10) {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/recommendations/${userId}`,
      {
        params: { limit },
      },
    );
    return response.data.recommendations;
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return [];
  }
}

// Get recommendations with location
async function getRecommendationsWithLocation(userId, userLat, userLng) {
  try {
    const response = await axios.get(
      `${API_BASE_URL}/recommendations/${userId}`,
      {
        params: {
          limit: 10,
          user_lat: userLat,
          user_lng: userLng,
          max_distance: 10,
        },
      },
    );
    return response.data.recommendations;
  } catch (error) {
    console.error("Error fetching recommendations:", error);
    return [];
  }
}
```

### Usage in Vue Component

```vue
<script>
import axios from "axios";
import { getCurrentUser } from "@/firebase/session";

export default {
  data() {
    return {
      recommendations: [],
      loading: false,
    };
  },
  async created() {
    await this.fetchRecommendations();
  },
  methods: {
    async fetchRecommendations() {
      this.loading = true;
      try {
        const user = await getCurrentUser();
        const response = await axios.get(
          `http://localhost:8000/recommendations/${user.uid}`,
          { params: { limit: 10 } },
        );
        this.recommendations = response.data.recommendations;
      } catch (error) {
        console.error("Error:", error);
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>
```

## Architecture

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application & routes
│   ├── firebase_service.py        # Firebase/Firestore integration
│   └── recommendation_engine.py   # Recommendation algorithms
├── requirements.txt
├── .env.example
└── README.md
```

## Algorithm Details

### Content-Based Scoring

Analyzes user's historical deal participation and calculates preference scores for each category. Deals matching user's preferred categories receive higher scores.

### Popularity Scoring

Uses logarithmic scaling based on `clickCount`:

- 0 clicks: 0.3
- 10 clicks: ~0.5
- 100 clicks: ~0.7
- 1000+ clicks: ~1.0

### Recency Scoring

Time-decay function:

- Last 24 hours: 1.0
- 1-3 days: 0.8
- 3-7 days: 0.6
- Older: 0.4

### Urgency Scoring

Based on time until expiration:

- <24 hours: 1.0 (urgent!)
- 1-3 days: 0.8
- 3-7 days: 0.6
- > 7 days: 0.4

## Performance Considerations

- Caching: Consider implementing Redis for caching recommendations
- Batch processing: Pre-compute recommendations for active users
- Database indexes: Ensure Firestore has proper indexes on `category`, `createdDateTime`, `validUntil`

## Future Enhancements

1. **Collaborative Filtering**: Implement user-user similarity for "users like you" recommendations
2. **A/B Testing**: Track which recommendation strategies perform best
3. **Real-time Updates**: Use Firebase listeners for live recommendations
4. **Machine Learning**: Train ML models on user behavior
5. **Personalized Ranking**: Learn individual user's ranking preferences
6. **Context-Aware**: Consider time of day, day of week for recommendations

## License

Part of the Save2Gether project.
