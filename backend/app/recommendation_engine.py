from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import Counter
import math
import numpy as np
from sklearn.decomposition import TruncatedSVD
from .firebase_service import FirebaseService


class RecommendationEngine:
    """
    Multi-strategy recommendation engine for deals.
    
    Strategies:
    1. Content-based: Recommend deals similar to user's past preferences
    2. Collaborative filtering: Recommend deals liked by similar users
    3. Popularity-based: Recommend trending/popular deals
    4. Location-based: Recommend nearby deals
    5. Recency-based: Recommend new deals
    """
    
    def __init__(self, firebase_service: FirebaseService):
        self.firebase = firebase_service
        self.categories = [
            "Food & Beverage",
            "Lifestyle & Fitness",
            "Travel & Attractions",
            "Retail",
            "Games & Entertainment"
        ]

        # SVD model state (in-memory)
        self.svd_model: Optional[TruncatedSVD] = None
        self.user_factors: Optional[np.ndarray] = None
        self.item_factors: Optional[np.ndarray] = None
        self.user_index: Dict[str, int] = {}
        self.item_index: Dict[str, int] = {}
        self.svd_ready: bool = False
        self.svd_last_trained_at: Optional[datetime] = None
        self.svd_n_components: int = 20
        self.svd_min_interactions: int = 5
        self.svd_retrain_interval = timedelta(minutes=30)

    def _extract_deal_id(self, deal_reference) -> Optional[str]:
        """Support Firestore refs, plain string IDs, and dict-like references."""
        if isinstance(deal_reference, str):
            return deal_reference
        if isinstance(deal_reference, dict):
            deal_id = deal_reference.get("id") or deal_reference.get("deal_id")
            if isinstance(deal_id, str):
                return deal_id
            return None
        return getattr(deal_reference, "id", None)

    async def train_svd_model(
        self,
        n_components: int = 20,
        min_interactions: int = 5
    ) -> Dict:
        """
        Train a collaborative filtering model using Truncated SVD on user-deal
        implicit interactions (joined deals).
        """
        all_users = await self.firebase.get_all_users()
        if not all_users:
            self._clear_svd_state()
            return {
                "trained": False,
                "reason": "No users available",
                "num_users": 0,
                "num_items": 0,
                "num_interactions": 0
            }

        interactions = []
        users_with_interactions = set()
        items_with_interactions = set()

        for user in all_users:
            user_id = user.get("id")
            if not user_id:
                continue

            deal_refs = user.get("deals", [])
            for deal_ref in deal_refs:
                deal_id = self._extract_deal_id(deal_ref)
                if not deal_id:
                    continue
                interactions.append((user_id, deal_id, 1.0))
                users_with_interactions.add(user_id)
                items_with_interactions.add(deal_id)

        num_interactions = len(interactions)
        if num_interactions < min_interactions:
            self._clear_svd_state()
            return {
                "trained": False,
                "reason": f"Not enough interactions (need >= {min_interactions})",
                "num_users": len(users_with_interactions),
                "num_items": len(items_with_interactions),
                "num_interactions": num_interactions
            }

        users = sorted(users_with_interactions)
        items = sorted(items_with_interactions)

        if len(users) < 2 or len(items) < 2:
            self._clear_svd_state()
            return {
                "trained": False,
                "reason": "Need at least 2 users and 2 deals",
                "num_users": len(users),
                "num_items": len(items),
                "num_interactions": num_interactions
            }

        user_index = {user_id: idx for idx, user_id in enumerate(users)}
        item_index = {deal_id: idx for idx, deal_id in enumerate(items)}

        interaction_matrix = np.zeros((len(users), len(items)), dtype=np.float32)
        for user_id, deal_id, value in interactions:
            interaction_matrix[user_index[user_id], item_index[deal_id]] = value

        max_components = min(len(users) - 1, len(items) - 1)
        effective_components = max(1, min(n_components, max_components))

        svd_model = TruncatedSVD(n_components=effective_components, random_state=42)
        user_factors = svd_model.fit_transform(interaction_matrix)
        item_factors = svd_model.components_.T

        self.svd_model = svd_model
        self.user_factors = user_factors
        self.item_factors = item_factors
        self.user_index = user_index
        self.item_index = item_index
        self.svd_ready = True
        self.svd_last_trained_at = datetime.now()
        self.svd_n_components = effective_components
        self.svd_min_interactions = min_interactions

        explained_variance = float(np.sum(svd_model.explained_variance_ratio_))

        return {
            "trained": True,
            "reason": "SVD model trained successfully",
            "num_users": len(users),
            "num_items": len(items),
            "num_interactions": num_interactions,
            "n_components": effective_components,
            "explained_variance": round(explained_variance, 4),
            "trained_at": self.svd_last_trained_at.isoformat()
        }

    def get_svd_status(self) -> Dict:
        """Return SVD model readiness and metadata."""
        return {
            "ready": self.svd_ready,
            "last_trained_at": self.svd_last_trained_at.isoformat() if self.svd_last_trained_at else None,
            "num_users": len(self.user_index),
            "num_items": len(self.item_index),
            "n_components": self.svd_n_components,
            "min_interactions": self.svd_min_interactions
        }

    async def _ensure_svd_model(self):
        """Train or refresh SVD model if needed."""
        needs_training = not self.svd_ready
        if self.svd_ready and self.svd_last_trained_at:
            needs_training = (datetime.now() - self.svd_last_trained_at) > self.svd_retrain_interval

        if needs_training:
            try:
                await self.train_svd_model(
                    n_components=self.svd_n_components,
                    min_interactions=self.svd_min_interactions
                )
            except Exception:
                self._clear_svd_state()

    def _clear_svd_state(self):
        self.svd_model = None
        self.user_factors = None
        self.item_factors = None
        self.user_index = {}
        self.item_index = {}
        self.svd_ready = False
        self.svd_last_trained_at = None

    def _calculate_svd_score(self, user_id: str, deal_id: str) -> float:
        """Predict user-deal affinity from latent factors."""
        if not self.svd_ready or self.user_factors is None or self.item_factors is None:
            return 0.0
        if user_id not in self.user_index or deal_id not in self.item_index:
            return 0.0

        user_idx = self.user_index[user_id]
        item_idx = self.item_index[deal_id]
        score = float(np.dot(self.user_factors[user_idx], self.item_factors[item_idx]))

        if score < 0:
            return 0.0
        return min(score, 1.0)
    
    async def get_recommendations(
        self,
        user_id: str,
        limit: int = 10,
        category_filter: Optional[str] = None,
        max_distance: Optional[float] = None,
        user_lat: Optional[float] = None,
        user_lng: Optional[float] = None
    ) -> List[Dict]:
        """
        Generate personalized recommendations using hybrid approach.
        """
        await self._ensure_svd_model()

        # Get user data and all available deals
        user = await self.firebase.get_user(user_id)
        if not user:
            return await self._get_default_recommendations(limit, category_filter)
        
        user_deals = await self.firebase.get_user_deals(user_id)
        all_deals = await self.firebase.get_deals(category=category_filter)
        
        # Filter out deals user already joined
        user_deal_ids = {deal['id'] for deal in user_deals}
        candidate_deals = [d for d in all_deals if d['id'] not in user_deal_ids]
        
        if not candidate_deals:
            return []
        
        # Calculate scores using different strategies
        scored_deals = []
        for deal in candidate_deals:
            score_components = {}

            # 0. SVD collaborative score
            svd_score = self._calculate_svd_score(user_id, deal.get('id', ''))
            if svd_score > 0:
                score_components['svd'] = svd_score
            
            # 1. Content-based score (based on user's category preferences)
            content_score = self._calculate_content_score(deal, user_deals)
            score_components['content'] = content_score
            
            # 2. Popularity score (based on clicks and groups)
            popularity_score = self._calculate_popularity_score(deal)
            score_components['popularity'] = popularity_score
            
            # 3. Recency score (newer deals get higher scores)
            recency_score = self._calculate_recency_score(deal)
            score_components['recency'] = recency_score
            
            # 4. Urgency score (deals expiring soon)
            urgency_score = self._calculate_urgency_score(deal)
            score_components['urgency'] = urgency_score
            
            # 5. Location score (if coordinates provided)
            location_score = 0.0
            if user_lat and user_lng and 'location' in deal:
                location_score = self._calculate_location_score(
                    deal, user_lat, user_lng, max_distance
                )
                score_components['location'] = location_score
            
            # Weighted combination of scores
            weights = {
                'svd': 0.35 if svd_score > 0 else 0.0,
                'content': 0.25,
                'popularity': 0.15,
                'recency': 0.10,
                'urgency': 0.10,
                'location': 0.05 if location_score > 0 else 0.0
            }

            total_weight = sum(w for w in weights.values() if w > 0)
            if total_weight > 0:
                for key, weight in weights.items():
                    if weight > 0:
                        weights[key] = weight / total_weight
            
            final_score = sum(score_components.get(k, 0) * w for k, w in weights.items())
            
            # Determine primary reason for recommendation
            reason = self._get_recommendation_reason(score_components, weights)
            
            scored_deals.append({
                **deal,
                'score': final_score,
                'score_components': score_components,
                'reason': reason
            })
        
        # Sort by score and return top N
        scored_deals.sort(key=lambda x: x['score'], reverse=True)
        recommendations = scored_deals[:limit]
        
        # Clean up response
        for rec in recommendations:
            rec['score'] = round(rec['score'], 3)
            if 'score_components' in rec:
                del rec['score_components']
        
        return recommendations
    
    def _calculate_content_score(self, deal: Dict, user_deals: List[Dict]) -> float:
        """Score based on user's category preferences"""
        if not user_deals:
            return 0.5  # Neutral score for new users
        
        # Count user's category preferences
        user_categories = [d.get('category') for d in user_deals if 'category' in d]
        category_counts = Counter(user_categories)
        
        if not category_counts:
            return 0.5
        
        total_deals = len(user_deals)
        deal_category = deal.get('category')
        
        if deal_category in category_counts:
            # Score based on percentage of user's deals in this category
            preference_score = category_counts[deal_category] / total_deals
            return min(preference_score * 2, 1.0)  # Scale up but cap at 1.0
        
        return 0.3  # Low score for categories user hasn't tried
    
    def _calculate_popularity_score(self, deal: Dict) -> float:
        """Score based on deal popularity (clicks)"""
        click_count = deal.get('clickCount', 0)
        
        # Normalize using logarithmic scale
        if click_count == 0:
            return 0.3
        
        # Score increases logarithmically with clicks
        score = min(math.log10(click_count + 1) / 3, 1.0)
        return max(score, 0.3)
    
    def _calculate_recency_score(self, deal: Dict) -> float:
        """Score based on how recently the deal was created"""
        if 'createdDateTime' not in deal:
            return 0.5
        
        created_time = deal['createdDateTime']
        if hasattr(created_time, 'timestamp'):
            created_dt = datetime.fromtimestamp(created_time.timestamp())
        else:
            return 0.5
        
        now = datetime.now()
        age_hours = (now - created_dt).total_seconds() / 3600
        
        # Deals created in last 24 hours get highest score
        if age_hours < 24:
            return 1.0
        elif age_hours < 72:  # 3 days
            return 0.8
        elif age_hours < 168:  # 1 week
            return 0.6
        else:
            return 0.4
    
    def _calculate_urgency_score(self, deal: Dict) -> float:
        """Score based on how soon the deal expires"""
        if 'validUntil' not in deal:
            return 0.5
        
        valid_until = deal['validUntil']
        if hasattr(valid_until, 'timestamp'):
            expiry_dt = datetime.fromtimestamp(valid_until.timestamp())
        else:
            return 0.5
        
        now = datetime.now()
        time_left = (expiry_dt - now).total_seconds() / 3600  # Hours until expiry
        
        if time_left < 0:
            return 0.0  # Expired
        elif time_left < 24:
            return 1.0  # Expiring soon - urgent!
        elif time_left < 72:
            return 0.8
        elif time_left < 168:  # 1 week
            return 0.6
        else:
            return 0.4
    
    def _calculate_location_score(
        self,
        deal: Dict,
        user_lat: float,
        user_lng: float,
        max_distance: Optional[float]
    ) -> float:
        """Score based on proximity to user (placeholder - needs geocoding)"""
        # This is a simplified version
        # In production, you'd use the actual location and calculate distance
        
        # For now, return a default score
        # TODO: Implement actual distance calculation using deal location
        return 0.7
    
    def _get_recommendation_reason(
        self,
        score_components: Dict[str, float],
        weights: Dict[str, float]
    ) -> str:
        """Determine the primary reason for recommending this deal"""
        weighted_scores = {k: score_components.get(k, 0) * weights.get(k, 0) 
                          for k in score_components}
        
        if not weighted_scores:
            return "Recommended for you"
        
        primary = max(weighted_scores.items(), key=lambda x: x[1])[0]
        
        reasons = {
            'svd': "Users with similar interests liked this",
            'content': "Matches your interests",
            'popularity': "Trending deal",
            'recency': "New deal",
            'urgency': "Expiring soon",
            'location': "Nearby"
        }
        
        return reasons.get(primary, "Recommended for you")
    
    async def _get_default_recommendations(
        self,
        limit: int,
        category_filter: Optional[str] = None
    ) -> List[Dict]:
        """Get default recommendations for new users"""
        deals = await self.firebase.get_deals(category=category_filter)
        
        # Score by popularity and recency
        for deal in deals:
            popularity = self._calculate_popularity_score(deal)
            recency = self._calculate_recency_score(deal)
            deal['score'] = (popularity * 0.6) + (recency * 0.4)
            deal['reason'] = "Popular deal"
        
        deals.sort(key=lambda x: x['score'], reverse=True)
        return deals[:limit]
    
    async def get_user_preferences(self, user_id: str) -> Dict:
        """Analyze and return user's inferred preferences"""
        user_deals = await self.firebase.get_user_deals(user_id)
        
        if not user_deals:
            return {
                "categories": {},
                "total_deals": 0,
                "favorite_category": None
            }
        
        # Category analysis
        categories = [d.get('category') for d in user_deals if 'category' in d]
        category_counts = Counter(categories)
        
        total = len(user_deals)
        category_percentages = {
            cat: round((count / total) * 100, 1)
            for cat, count in category_counts.items()
        }
        
        favorite = max(category_counts.items(), key=lambda x: x[1])[0] if category_counts else None
        
        return {
            "categories": category_percentages,
            "total_deals": total,
            "favorite_category": favorite,
            "category_counts": dict(category_counts)
        }
    
    async def get_collaborative_recommendations(
        self,
        user_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Collaborative filtering: find similar users and recommend their deals.
        This is more computationally expensive and should be used selectively.
        """
        # Get current user's deals
        user_deals = await self.firebase.get_user_deals(user_id)
        user_deal_ids = {d['id'] for d in user_deals}
        
        # Get all users
        all_users = await self.firebase.get_all_users()
        
        # Find similar users (users with overlapping deals)
        similar_users = []
        for other_user in all_users:
            if other_user['id'] == user_id:
                continue
            
            other_deals = other_user.get('deals', [])
            other_deal_ids = {
                deal_id
                for deal_id in (self._extract_deal_id(ref) for ref in other_deals)
                if deal_id
            }
            
            # Calculate similarity (Jaccard similarity)
            if not user_deal_ids or not other_deal_ids:
                continue
            
            intersection = len(user_deal_ids & other_deal_ids)
            union = len(user_deal_ids | other_deal_ids)
            similarity = intersection / union if union > 0 else 0
            
            if similarity > 0:
                similar_users.append({
                    'user_id': other_user['id'],
                    'similarity': similarity,
                    'deal_ids': other_deal_ids
                })
        
        # Sort by similarity
        similar_users.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Get deals from similar users that current user hasn't joined
        recommended_deal_ids = set()
        for similar_user in similar_users[:5]:  # Top 5 similar users
            new_deals = similar_user['deal_ids'] - user_deal_ids
            recommended_deal_ids.update(new_deals)
        
        # Fetch and return these deals
        recommendations = []
        for deal_id in list(recommended_deal_ids)[:limit]:
            deal = await self.firebase.get_deal(deal_id)
            if deal:
                deal['reason'] = "Users like you joined this"
                recommendations.append(deal)
        
        return recommendations
