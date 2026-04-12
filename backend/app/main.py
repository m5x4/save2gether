from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
from .recommendation_engine import RecommendationEngine
from .firebase_service import FirebaseService
import os
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Save2Gether Recommendation API",
    description="Deal recommendation service for Save2Gether platform",
    version="1.0.0"
)

# CORS Configuration
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

firebase_service = FirebaseService()
recommendation_engine = RecommendationEngine(firebase_service)


@app.on_event("startup")
async def startup_event():
    """Initialize SVD model on startup"""
    logger.info("Starting up Save2Gether Recommendation API...")
    try:
        result = await recommendation_engine.train_svd_model()
        if result.get("trained"):
            logger.info(f"SVD model trained successfully: {result}")
        else:
            logger.warning(f"SVD model training skipped: {result.get('reason')}")
    except Exception as e:
        logger.error(f"Error training SVD model on startup: {e}", exc_info=True)


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Save2Gether Recommendation API...")


class RecommendationRequest(BaseModel):
    user_id: str
    limit: Optional[int] = 10
    category: Optional[str] = None
    max_distance: Optional[float] = None
    user_lat: Optional[float] = None
    user_lng: Optional[float] = None


class SVDTrainRequest(BaseModel):
    n_components: Optional[int] = 20
    min_interactions: Optional[int] = 5


class DealResponse(BaseModel):
    id: str
    dealName: str
    merchantName: str
    category: str
    location: str
    numRequired: int
    validUntil: str
    score: float
    reason: str


@app.get("/")
async def root():
    return {
        "message": "Save2Gether Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "/recommendations/{user_id}": "Get personalized deal recommendations",
            "/model/svd/status": "Get SVD model status",
            "/model/svd/train": "Train/retrain SVD model",
            "/deals": "Get all available deals",
            "/health": "Health check"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    svd_status = recommendation_engine.get_svd_status()
    return {
        "status": "healthy",
        "service": "recommendation-api",
        "svd_model_ready": svd_status.get("ready", False)
    }


@app.get("/recommendations/{user_id}")
async def get_recommendations(
    user_id: str,
    limit: int = 10,
    category: Optional[str] = None,
    max_distance: Optional[float] = None,
    user_lat: Optional[float] = None,
    user_lng: Optional[float] = None
):
    """
    Get personalized deal recommendations for a user.
    
    Parameters:
    - user_id: The user's Firebase ID
    - limit: Maximum number of recommendations (default: 10)
    - category: Filter by category (optional)
    - max_distance: Maximum distance in km (optional)
    - user_lat: User's latitude for distance calculation (optional)
    - user_lng: User's longitude for distance calculation (optional)
    """
    try:
        logger.info(f"Fetching recommendations for user: {user_id}, limit: {limit}")
        recommendations = await recommendation_engine.get_recommendations(
            user_id=user_id,
            limit=limit,
            category_filter=category,
            max_distance=max_distance,
            user_lat=user_lat,
            user_lng=user_lng
        )
        logger.info(f"Found {len(recommendations)} recommendations for user {user_id}")
        return {
            "user_id": user_id,
            "count": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        logger.error(f"Error fetching recommendations for {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recommendations")
async def get_recommendations_post(request: RecommendationRequest):
    """
    Get personalized deal recommendations (POST version for complex requests).
    """
    try:
        recommendations = await recommendation_engine.get_recommendations(
            user_id=request.user_id,
            limit=request.limit,
            category_filter=request.category,
            max_distance=request.max_distance,
            user_lat=request.user_lat,
            user_lng=request.user_lng
        )
        return {
            "user_id": request.user_id,
            "count": len(recommendations),
            "recommendations": recommendations
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/deals")
async def get_all_deals(
    category: Optional[str] = None,
    limit: Optional[int] = 50
):
    """
    Get all available deals with optional filtering.
    """
    try:
        deals = await firebase_service.get_deals(category=category, limit=limit)
        return {
            "count": len(deals),
            "deals": deals
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/user/{user_id}/preferences")
async def get_user_preferences(user_id: str):
    """
    Get user's inferred preferences based on their activity.
    """
    try:
        preferences = await recommendation_engine.get_user_preferences(user_id)
        return {
            "user_id": user_id,
            "preferences": preferences
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/model/svd/status")
async def get_svd_status():
    """Get current SVD model status and metadata."""
    try:
        return recommendation_engine.get_svd_status()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/model/svd/train")
async def train_svd_model(request: SVDTrainRequest):
    """Train or retrain the SVD recommendation model."""
    try:
        logger.info(f"Training SVD model with n_components={request.n_components}, min_interactions={request.min_interactions}")
        result = await recommendation_engine.train_svd_model(
            n_components=request.n_components or 20,
            min_interactions=request.min_interactions or 5
        )
        logger.info(f"SVD training result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error training SVD model: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(app, host=host, port=port)
