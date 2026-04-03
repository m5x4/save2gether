import unittest
from datetime import datetime, timedelta

from app.recommendation_engine import RecommendationEngine


class FakeRef:
    def __init__(self, deal_id: str):
        self.id = deal_id


class FakeTimestamp:
    def __init__(self, dt: datetime):
        self._dt = dt

    def timestamp(self):
        return self._dt.timestamp()


class MockFirebaseService:
    def __init__(self):
        now = datetime.now()

        self.users = {
            "u1": {"id": "u1", "deals": [FakeRef("d1"), FakeRef("d2")]},
            "u2": {"id": "u2", "deals": [FakeRef("d1"), FakeRef("d3")]},
            "u3": {"id": "u3", "deals": [FakeRef("d2"), FakeRef("d4")]},
            "cold": {"id": "cold", "deals": []},
        }

        self.deals = {
            "d1": {
                "id": "d1",
                "category": "Food & Beverage",
                "clickCount": 100,
                "createdDateTime": FakeTimestamp(now - timedelta(hours=8)),
                "validUntil": FakeTimestamp(now + timedelta(days=2)),
                "location": "A",
            },
            "d2": {
                "id": "d2",
                "category": "Food & Beverage",
                "clickCount": 30,
                "createdDateTime": FakeTimestamp(now - timedelta(days=2)),
                "validUntil": FakeTimestamp(now + timedelta(days=4)),
                "location": "B",
            },
            "d3": {
                "id": "d3",
                "category": "Retail",
                "clickCount": 80,
                "createdDateTime": FakeTimestamp(now - timedelta(hours=20)),
                "validUntil": FakeTimestamp(now + timedelta(hours=10)),
                "location": "C",
            },
            "d4": {
                "id": "d4",
                "category": "Travel & Attractions",
                "clickCount": 12,
                "createdDateTime": FakeTimestamp(now - timedelta(days=5)),
                "validUntil": FakeTimestamp(now + timedelta(days=7)),
                "location": "D",
            },
            "d5": {
                "id": "d5",
                "category": "Retail",
                "clickCount": 40,
                "createdDateTime": FakeTimestamp(now - timedelta(hours=15)),
                "validUntil": FakeTimestamp(now + timedelta(days=3)),
                "location": "E",
            },
        }

    async def get_user(self, user_id):
        return self.users.get(user_id)

    async def get_user_deals(self, user_id):
        user = self.users.get(user_id)
        if not user:
            return []
        deal_refs = user.get("deals", [])
        return [self.deals[deal_ref.id] for deal_ref in deal_refs if deal_ref.id in self.deals]

    async def get_deal(self, deal_id):
        return self.deals.get(deal_id)

    async def get_deals(self, category=None, limit=100):
        deals = list(self.deals.values())
        if category:
            deals = [deal for deal in deals if deal.get("category") == category]
        return deals[:limit]

    async def get_all_users(self, limit=1000):
        return list(self.users.values())[:limit]


class RecommendationEngineSVDTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.firebase = MockFirebaseService()
        self.engine = RecommendationEngine(self.firebase)

    async def test_train_svd_model_success(self):
        result = await self.engine.train_svd_model(n_components=2, min_interactions=3)

        self.assertTrue(result["trained"])
        self.assertEqual(result["n_components"], 2)
        self.assertTrue(self.engine.svd_ready)
        self.assertGreaterEqual(result["num_interactions"], 3)

    async def test_train_svd_model_not_enough_interactions(self):
        result = await self.engine.train_svd_model(n_components=3, min_interactions=50)

        self.assertFalse(result["trained"])
        self.assertFalse(self.engine.svd_ready)

    async def test_recommendations_use_svd_when_available(self):
        await self.engine.train_svd_model(n_components=2, min_interactions=3)
        recommendations = await self.engine.get_recommendations(user_id="u1", limit=5)

        self.assertTrue(len(recommendations) > 0)
        self.assertTrue(all(rec["id"] not in {"d1", "d2"} for rec in recommendations))
        self.assertTrue(all("score" in rec for rec in recommendations))

    async def test_status_contains_training_metadata(self):
        await self.engine.train_svd_model(n_components=2, min_interactions=3)
        status = self.engine.get_svd_status()

        self.assertTrue(status["ready"])
        self.assertEqual(status["n_components"], 2)
        self.assertIsNotNone(status["last_trained_at"])


if __name__ == "__main__":
    unittest.main()
