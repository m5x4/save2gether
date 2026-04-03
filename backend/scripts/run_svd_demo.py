import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional

BACKEND_ROOT = Path(__file__).resolve().parent.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.recommendation_engine import RecommendationEngine


class InMemoryDataService:
    def __init__(self, users: List[Dict], deals: List[Dict]):
        self.users_by_id = {user["id"]: user for user in users if "id" in user}
        self.deals_by_id = {deal["id"]: deal for deal in deals if "id" in deal}

    async def get_user(self, user_id: str) -> Optional[Dict]:
        return self.users_by_id.get(user_id)

    async def get_all_users(self, limit: int = 1000) -> List[Dict]:
        users = list(self.users_by_id.values())
        return users[:limit]

    async def get_deal(self, deal_id: str) -> Optional[Dict]:
        return self.deals_by_id.get(deal_id)

    async def get_deals(self, category: Optional[str] = None, limit: int = 100) -> List[Dict]:
        deals = list(self.deals_by_id.values())
        if category:
            deals = [deal for deal in deals if deal.get("category") == category]
        return deals[:limit]

    async def get_user_deals(self, user_id: str) -> List[Dict]:
        user = self.users_by_id.get(user_id)
        if not user:
            return []

        deal_refs = user.get("deals", [])
        resolved = []
        for deal_ref in deal_refs:
            if isinstance(deal_ref, str):
                deal_id = deal_ref
            elif isinstance(deal_ref, dict):
                deal_id = deal_ref.get("id") or deal_ref.get("deal_id")
            else:
                deal_id = getattr(deal_ref, "id", None)

            if deal_id and deal_id in self.deals_by_id:
                resolved.append(self.deals_by_id[deal_id])

        return resolved


def load_json(path: Path) -> List[Dict]:
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    if not isinstance(data, list):
        raise ValueError(f"Expected list in {path}, got {type(data).__name__}")
    return data


def select_user_id(users: List[Dict], explicit_user_id: Optional[str] = None) -> str:
    if explicit_user_id:
        return explicit_user_id

    users_with_interactions = [u for u in users if len(u.get("deals", [])) > 0]
    if users_with_interactions:
        return users_with_interactions[0]["id"]

    if not users:
        raise ValueError("No users available in users.json")

    return users[0]["id"]


async def run_demo(
    data_dir: Path,
    user_id: Optional[str],
    limit: int,
    n_components: int,
    min_interactions: int,
    category: Optional[str],
):
    users_path = data_dir / "users.json"
    deals_path = data_dir / "deals.json"

    if not users_path.exists() or not deals_path.exists():
        raise FileNotFoundError(
            f"Missing users.json/deals.json in {data_dir}. "
            "Run generate_simulated_training_data.py first."
        )

    users = load_json(users_path)
    deals = load_json(deals_path)
    target_user_id = select_user_id(users, user_id)

    service = InMemoryDataService(users, deals)
    engine = RecommendationEngine(service)

    print("=== SVD Training ===")
    train_result = await engine.train_svd_model(
        n_components=n_components,
        min_interactions=min_interactions,
    )
    print(json.dumps(train_result, indent=2))

    if not train_result.get("trained"):
        print("\nTraining did not succeed; no recommendation run.")
        return

    print("\n=== SVD Status ===")
    print(json.dumps(engine.get_svd_status(), indent=2))

    print("\n=== Recommendations ===")
    recommendations = await engine.get_recommendations(
        user_id=target_user_id,
        limit=limit,
        category_filter=category,
    )

    if not recommendations:
        print(f"No recommendations for user '{target_user_id}'.")
        return

    print(f"User: {target_user_id} | Returned: {len(recommendations)}")
    for idx, rec in enumerate(recommendations, start=1):
        print(
            f"{idx}. {rec.get('id')} | {rec.get('dealName', 'Unknown Deal')} | "
            f"score={rec.get('score')} | reason={rec.get('reason')}"
        )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run end-to-end SVD training and recommendation demo using local JSON data."
    )
    parser.add_argument(
        "--data-dir",
        default="generated_data",
        help="Directory containing users.json and deals.json",
    )
    parser.add_argument("--user-id", default=None, help="User ID to generate recommendations for")
    parser.add_argument("--limit", type=int, default=10, help="Number of recommendations")
    parser.add_argument("--n-components", type=int, default=20, help="SVD latent dimensions")
    parser.add_argument(
        "--min-interactions",
        type=int,
        default=5,
        help="Minimum interactions needed before training succeeds",
    )
    parser.add_argument("--category", default=None, help="Optional category filter")

    args = parser.parse_args()

    if args.limit <= 0:
        raise ValueError("--limit must be > 0")
    if args.n_components <= 0:
        raise ValueError("--n-components must be > 0")
    if args.min_interactions <= 0:
        raise ValueError("--min-interactions must be > 0")

    return args


def main():
    args = parse_args()
    data_dir = Path(args.data_dir)
    asyncio.run(
        run_demo(
            data_dir=data_dir,
            user_id=args.user_id,
            limit=args.limit,
            n_components=args.n_components,
            min_interactions=args.min_interactions,
            category=args.category,
        )
    )


if __name__ == "__main__":
    main()
