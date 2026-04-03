import firebase_admin
from firebase_admin import credentials, firestore
from typing import List, Dict, Optional
from datetime import datetime
import os


class FirebaseService:
    def __init__(self):
        self._init_firebase()
        self.db = firestore.client()
    
    def _init_firebase(self):
        """Initialize Firebase Admin SDK"""
        if not firebase_admin._apps:
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
            else:
                firebase_admin.initialize_app()
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Fetch user data from Firestore"""
        try:
            user_ref = self.db.collection('User').document(user_id)
            user_doc = user_ref.get()
            if user_doc.exists:
                return {"id": user_doc.id, **user_doc.to_dict()}
            return None
        except Exception as e:
            print(f"Error fetching user {user_id}: {e}")
            return None
    
    async def get_user_deals(self, user_id: str) -> List[Dict]:
        """Get all deals a user has participated in"""
        try:
            user = await self.get_user(user_id)
            if not user or 'deals' not in user:
                return []
            
            deal_refs = user['deals']
            deals = []
            for deal_ref in deal_refs:
                deal_id = deal_ref.id
                deal = await self.get_deal(deal_id)
                if deal:
                    deals.append(deal)
            return deals
        except Exception as e:
            print(f"Error fetching user deals: {e}")
            return []
    
    async def get_deal(self, deal_id: str) -> Optional[Dict]:
        """Fetch a single deal by ID"""
        try:
            deal_ref = self.db.collection('Deal').document(deal_id)
            deal_doc = deal_ref.get()
            if deal_doc.exists:
                data = deal_doc.to_dict()
                return {"id": deal_doc.id, **data}
            return None
        except Exception as e:
            print(f"Error fetching deal {deal_id}: {e}")
            return None
    
    async def get_deals(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        """Fetch all deals with optional filtering"""
        try:
            query = self.db.collection('Deal')
            
            if category:
                query = query.where('category', '==', category)
            
            query = query.limit(limit)
            deals_docs = query.stream()
            
            deals = []
            current_time = datetime.now()
            
            for doc in deals_docs:
                data = doc.to_dict()
                # Filter out expired deals
                if 'validUntil' in data:
                    valid_until = data['validUntil']
                    if hasattr(valid_until, 'timestamp'):
                        expiry_date = datetime.fromtimestamp(valid_until.timestamp())
                        if expiry_date < current_time:
                            continue
                
                deals.append({"id": doc.id, **data})
            
            return deals
        except Exception as e:
            print(f"Error fetching deals: {e}")
            return []
    
    async def get_user_reviews(self, user_id: str) -> List[Dict]:
        """Get all reviews written by a user"""
        try:
            reviews_ref = self.db.collection('User').document(user_id).collection('Review')
            reviews_docs = reviews_ref.stream()
            
            reviews = []
            for doc in reviews_docs:
                reviews.append({"id": doc.id, **doc.to_dict()})
            
            return reviews
        except Exception as e:
            print(f"Error fetching user reviews: {e}")
            return []
    
    async def get_all_users(self, limit: int = 1000) -> List[Dict]:
        """Get all users for collaborative filtering"""
        try:
            users_ref = self.db.collection('User').limit(limit)
            users_docs = users_ref.stream()
            
            users = []
            for doc in users_docs:
                users.append({"id": doc.id, **doc.to_dict()})
            
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []
    
    async def update_deal_recommendation_score(self, deal_id: str, score: float):
        """Update deal with recommendation score (for analytics)"""
        try:
            deal_ref = self.db.collection('Deal').document(deal_id)
            deal_ref.update({
                'lastRecommendationScore': score,
                'lastRecommendedAt': firestore.SERVER_TIMESTAMP
            })
        except Exception as e:
            print(f"Error updating deal score: {e}")
