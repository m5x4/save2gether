#!/usr/bin/env python3
"""
Demo client for Save2Gether Recommendation API
Shows how to use the API endpoints
"""

import asyncio
import aiohttp
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

async def get_recommendations(
    user_id: str,
    limit: int = 10,
    category: Optional[str] = None,
    lat: Optional[float] = None,
    lng: Optional[float] = None
):
    """Get recommendations for a user"""
    async with aiohttp.ClientSession() as session:
        params = {
            "limit": limit,
            "category": category,
            "user_lat": lat,
            "user_lng": lng
        }
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        async with session.get(f"{BASE_URL}/recommendations/{user_id}", params=params) as resp:
            data = await resp.json()
            return data

async def get_all_deals(category: Optional[str] = None, limit: int = 50):
    """Get all available deals"""
    async with aiohttp.ClientSession() as session:
        params = {"limit": limit}
        if category:
            params["category"] = category
            
        async with session.get(f"{BASE_URL}/deals", params=params) as resp:
            data = await resp.json()
            return data

async def check_health():
    """Check API health"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/health") as resp:
            data = await resp.json()
            return data

async def get_svd_status():
    """Get SVD model status"""
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{BASE_URL}/model/svd/status") as resp:
            data = await resp.json()
            return data

async def train_svd(n_components: int = 20, min_interactions: int = 5):
    """Train SVD model"""
    async with aiohttp.ClientSession() as session:
        payload = {
            "n_components": n_components,
            "min_interactions": min_interactions
        }
        async with session.post(f"{BASE_URL}/model/svd/train", json=payload) as resp:
            data = await resp.json()
            return data

async def main():
    """Run demo"""
    print("🚀 Save2Gether Recommendation API Demo\n")
    
    # Check health
    print("1️⃣  Checking API health...")
    try:
        health = await check_health()
        print(f"   ✅ API Status: {health['status']}")
        print(f"   ✅ SVD Model Ready: {health.get('svd_model_ready', False)}\n")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print("   Make sure the API is running: python -m uvicorn app.main:app --reload\n")
        return
    
    # Get SVD status
    print("2️⃣  Checking SVD model status...")
    try:
        svd_status = await get_svd_status()
        print(f"   SVD Ready: {svd_status.get('svd_ready', False)}")
        print(f"   Users with interactions: {svd_status.get('num_users_trained', 0)}")
        print(f"   Deals: {svd_status.get('num_items_trained', 0)}\n")
    except Exception as e:
        print(f"   ⚠️  {e}\n")
    
    # Get all deals
    print("3️⃣  Fetching available deals...")
    try:
        deals = await get_all_deals(limit=5)
        print(f"   Found {deals['count']} deals")
        for deal in deals['deals'][:3]:
            print(f"   • {deal.get('dealName', 'N/A')} - {deal.get('category', 'N/A')}")
        print()
    except Exception as e:
        print(f"   ⚠️  {e}\n")
    
    # Get recommendations for a test user
    # Note: Replace with an actual user ID from your Firestore
    print("4️⃣  Getting recommendations for a user...")
    print("   📝 Note: Replace 'test_user_id' with an actual user ID from your database\n")
    
    test_user_id = "test_user_id"
    try:
        recs = await get_recommendations(test_user_id, limit=5)
        print(f"   Found {recs['count']} recommendations")
        for rec in recs['recommendations'][:3]:
            print(f"   • {rec.get('dealName', 'N/A')} (score: {rec.get('score', 0):.2f})")
            print(f"     Reason: {rec.get('reason', 'N/A')}\n")
    except Exception as e:
        print(f"   Note: {e}\n")
    
    print("✅ Demo complete! Check http://localhost:8000/docs for interactive API documentation")

if __name__ == "__main__":
    asyncio.run(main())
