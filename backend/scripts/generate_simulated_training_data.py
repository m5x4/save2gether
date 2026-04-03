import argparse
import csv
import json
import random
import shutil
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Tuple


CATEGORIES = [
    "Food & Beverage",
    "Lifestyle & Fitness",
    "Travel & Attractions",
    "Retail",
    "Games & Entertainment",
]

MERCHANTS_BY_CATEGORY = {
    "Food & Beverage": ["Bistro Haven", "Sizzle Spot", "Urban Bites", "The Daily Roast"],
    "Lifestyle & Fitness": ["Core Studio", "Pulse Lab", "Zen Motion", "Peak Fitness"],
    "Travel & Attractions": ["City Escapes", "Roam Easy", "Skyline Tours", "Island Hopper"],
    "Retail": ["Trend Basket", "Value Mart", "Urban Closet", "Smart Goods"],
    "Games & Entertainment": ["FunHub", "Pixel Arcade", "Play District", "Game Vault"],
}

LOCATION_AREAS = [
    "Orchard", "Jurong", "Tampines", "Woodlands", "Bishan", "Paya Lebar", "Clementi"
]


@dataclass
class GenerationConfig:
    output_dir: Path
    num_users: int
    num_deals: int
    min_interactions: int
    max_interactions: int
    cold_start_ratio: float
    seed: int


def _iso(dt: datetime) -> str:
    utc_dt = dt.astimezone(timezone.utc).replace(microsecond=0)
    return utc_dt.isoformat().replace("+00:00", "Z")


def _weighted_sample_without_replacement(
    rng: random.Random,
    items: List[Dict],
    weights: List[float],
    k: int,
) -> List[Dict]:
    if k <= 0 or not items:
        return []

    selected = []
    pool_items = list(items)
    pool_weights = list(weights)

    for _ in range(min(k, len(pool_items))):
        chosen = rng.choices(pool_items, weights=pool_weights, k=1)[0]
        idx = pool_items.index(chosen)
        selected.append(chosen)
        pool_items.pop(idx)
        pool_weights.pop(idx)

    return selected


def generate_deals(config: GenerationConfig, rng: random.Random) -> List[Dict]:
    now = datetime.now(timezone.utc)
    deals = []

    for idx in range(1, config.num_deals + 1):
        category = rng.choice(CATEGORIES)
        merchant = rng.choice(MERCHANTS_BY_CATEGORY[category])
        created_at = now - timedelta(days=rng.randint(0, 60), hours=rng.randint(0, 23))
        valid_until = now + timedelta(days=rng.randint(1, 45), hours=rng.randint(0, 23))

        click_count = int(rng.lognormvariate(3.0, 0.9))
        click_count = max(0, min(click_count, 3000))

        deals.append(
            {
                "id": f"deal_{idx:05d}",
                "dealName": f"{category} Promo #{idx}",
                "merchantName": merchant,
                "category": category,
                "location": f"{rng.choice(LOCATION_AREAS)}, Singapore",
                "numRequired": rng.randint(2, 12),
                "clickCount": click_count,
                "createdDateTime": _iso(created_at),
                "validUntil": _iso(valid_until),
            }
        )

    return deals


def generate_users_and_interactions(
    config: GenerationConfig,
    deals: List[Dict],
    rng: random.Random,
) -> Tuple[List[Dict], List[Dict]]:
    users = []
    interactions = []
    now = datetime.now(timezone.utc)

    deals_by_category: Dict[str, List[Dict]] = {category: [] for category in CATEGORIES}
    for deal in deals:
        deals_by_category[deal["category"]].append(deal)

    for user_idx in range(1, config.num_users + 1):
        user_id = f"user_{user_idx:05d}"
        preferred_categories = rng.sample(CATEGORIES, k=rng.choice([1, 1, 2]))

        is_cold_start = rng.random() < config.cold_start_ratio
        interaction_count = 0
        if not is_cold_start:
            interaction_count = rng.randint(config.min_interactions, config.max_interactions)

        category_pool = []
        for category in preferred_categories:
            category_pool.extend(deals_by_category.get(category, []))

        if len(category_pool) < interaction_count:
            category_pool = deals

        weights = [1.0 + (deal.get("clickCount", 0) / 250.0) for deal in category_pool]
        selected_deals = _weighted_sample_without_replacement(rng, category_pool, weights, interaction_count)

        deal_ids = []
        for deal in selected_deals:
            deal_ids.append(deal["id"])
            joined_at = now - timedelta(days=rng.randint(0, 120), hours=rng.randint(0, 23))
            interactions.append(
                {
                    "user_id": user_id,
                    "deal_id": deal["id"],
                    "interaction": 1.0,
                    "joinedAt": _iso(joined_at),
                }
            )

        users.append(
            {
                "id": user_id,
                "name": f"User {user_idx}",
                "preferredCategories": preferred_categories,
                "deals": deal_ids,
            }
        )

    return users, interactions


def build_dataset(config: GenerationConfig) -> Dict:
    rng = random.Random(config.seed)
    deals = generate_deals(config, rng)
    users, interactions = generate_users_and_interactions(config, deals, rng)

    category_counts = Counter(deal["category"] for deal in deals)
    user_interaction_counts = [len(user["deals"]) for user in users]

    metadata = {
        "generatedAt": _iso(datetime.now(timezone.utc)),
        "seed": config.seed,
        "numUsers": len(users),
        "numDeals": len(deals),
        "numInteractions": len(interactions),
        "coldStartUsers": sum(1 for c in user_interaction_counts if c == 0),
        "avgInteractionsPerUser": round(sum(user_interaction_counts) / max(1, len(user_interaction_counts)), 2),
        "dealsByCategory": dict(category_counts),
    }

    return {
        "metadata": metadata,
        "users": users,
        "deals": deals,
        "interactions": interactions,
    }


def write_outputs(config: GenerationConfig, dataset: Dict):
    if config.output_dir.exists():
        shutil.rmtree(config.output_dir)
    config.output_dir.mkdir(parents=True, exist_ok=True)

    all_path = config.output_dir / "simulated_training_dataset.json"
    users_path = config.output_dir / "users.json"
    deals_path = config.output_dir / "deals.json"
    interactions_path = config.output_dir / "interactions.csv"

    with all_path.open("w", encoding="utf-8") as fp:
        json.dump(dataset, fp, indent=2)

    with users_path.open("w", encoding="utf-8") as fp:
        json.dump(dataset["users"], fp, indent=2)

    with deals_path.open("w", encoding="utf-8") as fp:
        json.dump(dataset["deals"], fp, indent=2)

    with interactions_path.open("w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["user_id", "deal_id", "interaction", "joinedAt"])
        writer.writeheader()
        writer.writerows(dataset["interactions"])

    print("Generated files:")
    print(f"- {all_path}")
    print(f"- {users_path}")
    print(f"- {deals_path}")
    print(f"- {interactions_path}")
    print("Summary:")
    for key, value in dataset["metadata"].items():
        print(f"  {key}: {value}")


def parse_args() -> GenerationConfig:
    parser = argparse.ArgumentParser(
        description="Generate simulated users/deals/interactions for SVD recommendation training."
    )
    parser.add_argument("--output-dir", default="generated_data", help="Directory for generated files")
    parser.add_argument("--num-users", type=int, default=200)
    parser.add_argument("--num-deals", type=int, default=300)
    parser.add_argument("--min-interactions", type=int, default=3)
    parser.add_argument("--max-interactions", type=int, default=20)
    parser.add_argument("--cold-start-ratio", type=float, default=0.15)
    parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args()

    if args.num_users <= 0 or args.num_deals <= 0:
        raise ValueError("num-users and num-deals must be > 0")
    if args.min_interactions < 0 or args.max_interactions < 0:
        raise ValueError("interaction bounds cannot be negative")
    if args.max_interactions < args.min_interactions:
        raise ValueError("max-interactions must be >= min-interactions")
    if not 0 <= args.cold_start_ratio <= 1:
        raise ValueError("cold-start-ratio must be between 0 and 1")

    return GenerationConfig(
        output_dir=Path(args.output_dir),
        num_users=args.num_users,
        num_deals=args.num_deals,
        min_interactions=args.min_interactions,
        max_interactions=args.max_interactions,
        cold_start_ratio=args.cold_start_ratio,
        seed=args.seed,
    )


def main():
    config = parse_args()
    dataset = build_dataset(config)
    write_outputs(config, dataset)


if __name__ == "__main__":
    main()
