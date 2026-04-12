# FastAPI Implementation - Setup Guide

## ✅ What's Been Done

1. **Updated FastAPI Configuration** (`app/main.py`)
   - Better CORS configuration (uses environment variables)
   - Logging setup for debugging
   - Startup/shutdown events
   - Error handling with detailed logging
   - All recommendation endpoints working

2. **Environment Configuration** (`.env`)
   - Local development settings
   - Firebase credentials path
   - CORS origins configuration
   - Recommendation engine settings

3. **Documentation & Scripts**
   - `API_README.md` - Complete API documentation
   - `start_api.sh` - Convenient startup script
   - `demo_client.py` - Example client to test the API

4. **Dependencies** (`requirements.txt`)
   - All packages ready (added aiohttp for demo client)

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
cd /Users/maximus/save2gether_2/backend
/opt/homebrew/bin/python3 -m pip install -r requirements.txt
```

### Step 2: Add Firebase Credentials

You need your Firebase service account JSON. Get it from:

1. Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save the JSON file as `backend/firebase-credentials.json`

Or set the path in `.env`:

```env
FIREBASE_CREDENTIALS_PATH=/path/to/your/firebase-key.json
```

### Step 3: Start the API

Option A - Using the startup script:

```bash
bash start_api.sh
```

Option B - Direct with uvicorn:

```bash
cd /Users/maximus/save2gether_2/backend
/opt/homebrew/bin/python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 4: Test the API

Once running, visit:

- 📚 **Interactive Docs**: http://localhost:8000/docs
- 🔍 **ReDoc**: http://localhost:8000/redoc
- 💚 **Health Check**: http://localhost:8000/health

## 📡 API Endpoints Reference

```
GET  /health                              - Health check
GET  /recommendations/{user_id}           - Get personalized recommendations
POST /recommendations                     - Get recommendations (POST with filters)
GET  /user/{user_id}/preferences          - Get inferred user preferences
GET  /deals                                - Get all available deals
GET  /model/svd/status                    - Check SVD model training status
POST /model/svd/train                     - Train/retrain SVD model
```

## 🧪 Testing with Demo Client

After API is running:

```bash
/opt/homebrew/bin/python3 demo_client.py
```

This will:

- ✅ Check API health
- ✅ Show SVD model status
- ✅ List available deals
- ✅ Get recommendations (if you have test users)

## 🔧 Configure for Your Frontend

Update `ALLOWED_ORIGINS` in `.env` to match your frontend URL:

```env
# For Vite dev server (default)
ALLOWED_ORIGINS=http://localhost:5173

# For production
ALLOWED_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
```

## 📝 Frontend Integration Example

### Vue.js / JavaScript

```javascript
// Get recommendations
const response = await fetch(
  "http://localhost:8000/recommendations/user123?limit=10",
);
const data = await response.json();
console.log(data.recommendations);
```

```javascript
// Using Fetch API
const getRecommendations = async (userId) => {
  try {
    const res = await fetch(
      `http://localhost:8000/recommendations/${userId}?limit=10`,
    );
    const data = await res.json();
    return data.recommendations;
  } catch (error) {
    console.error("Failed to fetch recommendations:", error);
  }
};
```

## 🚢 Deployment Checklist

- [ ] Firebase credentials configured
- [ ] `ALLOWED_ORIGINS` set to your production domain
- [ ] Environment variables set on deployment platform
- [ ] Test health endpoint: `/health`
- [ ] Test recommendations endpoint with real user ID
- [ ] Monitor logs for errors

## 🐛 Troubleshooting

### "Python command not found"

Use `/opt/homebrew/bin/python3` explicitly

### "Firebase credentials not found"

- Ensure `firebase-credentials.json` is in `backend/` directory
- Or set `FIREBASE_CREDENTIALS_PATH` in `.env`

### "Port 8000 already in use"

Change port in `.env` or command:

```bash
/opt/homebrew/bin/python3 -m uvicorn app.main:app --port 8001
```

### "No recommendations returned"

- Check SVD model status: `GET /model/svd/status`
- Ensure your Firestore has users with joined deals
- Minimum 5 interactions needed by default

## 📚 Next Steps

1. **Integrate with Frontend** - Update your Vue components to call the API
2. **Add Rate Limiting** - Prevent API abuse (install `slowapi`)
3. **Add Authentication** - Secure endpoints with Firebase Auth
4. **Setup Logging** - Store logs to file or cloud service
5. **Deploy** - Use Docker, Railway, Google Cloud Run, etc.

## 🎯 API Response Example

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
      "location": "123 Main St, City",
      "numRequired": 4,
      "validUntil": "2026-04-20T23:59:59",
      "score": 0.87,
      "reason": "Users with similar interests liked this"
    },
    {
      "id": "deal_789",
      "dealName": "Free Coffee",
      "merchantName": "Bean & Brew",
      "category": "Food & Beverage",
      "location": "456 Oak Ave, City",
      "numRequired": 2,
      "validUntil": "2026-04-25T23:59:59",
      "score": 0.76,
      "reason": "Matches your interests"
    }
  ]
}
```

---

**Questions?** Check the full documentation in `API_README.md`
