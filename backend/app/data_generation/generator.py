
import json
import random
from pathlib import Path

import numpy as np
import pandas as pd
from faker import Faker


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT_DIR / "config" / "generator_config.json"

CATEGORIES = [
    "Beauty", "Skincare", "Fashion", "Fitness", "Food",
    "Travel", "Technology", "Home", "Lifestyle", "Gaming"
]

PLATFORMS = ["Instagram", "YouTube", "TikTok"]
OBJECTIVES = ["Awareness", "Engagement", "Conversions", "Sales"]

LOCATIONS = [
    "India", "United States", "United Kingdom", "Canada",
    "Australia", "Germany", "France", "Singapore"
]

INTERESTS = [
    "skincare", "beauty", "fashion", "fitness", "travel",
    "food", "technology", "sustainability", "luxury",
    "gaming", "wellness", "home decor", "parenting"
]


def load_config(config_path=None):
    path = Path(config_path) if config_path else DEFAULT_CONFIG

    with path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    counts = config.get("record_counts", {})
    required = [
        "influencers", "audience_segments", "brands",
        "products", "brand_affinity", "campaigns",
        "campaign_performance"
    ]

    for name in required:
        if int(counts.get(name, 0)) < 1:
            raise ValueError(
                f"record_counts.{name} must be greater than zero"
            )

    formats = config.get("formats", ["csv", "parquet"])
    if not formats or any(
        fmt not in {"csv", "parquet"} for fmt in formats
    ):
        raise ValueError("formats must contain csv and/or parquet")

    if int(config.get("seed", 42)) < 0:
        raise ValueError("seed must be non-negative")

    return config


def generate_datasets(config_path=None, output_dir=None, formats=None):
    config = load_config(config_path)
    counts = config["record_counts"]
    seed = int(config.get("seed", 42))

    random.seed(seed)
    np.random.seed(seed)
    rng = np.random.default_rng(seed)

    fake = Faker("en_US")
    Faker.seed(seed)

    # ---------------------------------------------------------
    # 1. Brands
    # ---------------------------------------------------------
    brands = []

    for i in range(counts["brands"]):
        category = CATEGORIES[i % len(CATEGORIES)]
        age_min = int(rng.integers(18, 31))

        brands.append({
            "brand_id": f"BR{i + 1:05d}",
            "brand_name": fake.company(),
            "primary_category": category,
            "target_age_min": age_min,
            "target_age_max": int(rng.integers(max(age_min, 35), 61)),
            "target_gender": random.choice(
                ["All", "Female", "Male"]
            ),
            "brand_tone": random.choice(
                ["Premium", "Affordable", "Innovative", "Sustainable"]
            )
        })

    brands_df = pd.DataFrame(brands)
    brand_records = brands_df.to_dict("records")
    brand_by_id = {
        row["brand_id"]: row for row in brand_records
    }

    # ---------------------------------------------------------
    # 2. Products
    # ---------------------------------------------------------
    products = []

    for i in range(counts["products"]):
        brand = random.choice(brand_records)

        products.append({
            "product_id": f"PR{i + 1:06d}",
            "brand_id": brand["brand_id"],
            "product_name": fake.catch_phrase(),
            "category": brand["primary_category"],
            "price": round(float(rng.uniform(10, 1000)), 2),
            "target_age_min": brand["target_age_min"],
            "target_age_max": brand["target_age_max"]
        })

    products_df = pd.DataFrame(products)
    product_records = products_df.to_dict("records")

    # ---------------------------------------------------------
    # 3. Influencers
    # ---------------------------------------------------------
    influencers = []

    for i in range(counts["influencers"]):
        followers = int(
            np.clip(rng.lognormal(mean=10.0, sigma=1.1), 1000, 5000000)
        )

        # Smaller creators generally have higher engagement.
        engagement_rate = float(
            np.clip(
                rng.normal(0.055 - min(followers / 5_000_000, 0.04),
                           0.012),
                0.005,
                0.12
            )
        )

        influencers.append({
            "influencer_id": f"IN{i + 1:06d}",
            "display_name": fake.name(),
            "platform": random.choice(PLATFORMS),
            "primary_niche": random.choice(CATEGORIES),
            "follower_count": followers,
            "engagement_rate": round(engagement_rate, 4),
            "location": random.choice(LOCATIONS),
            "average_rate": round(
                float(max(50, followers * rng.uniform(0.002, 0.02))),
                2
            ),
            "verified": bool(rng.random() < 0.2)
        })

    influencers_df = pd.DataFrame(influencers)
    influencer_records = influencers_df.to_dict("records")

    
    # ---------------------------------------------------------
    # 4. Audience segments
    # ---------------------------------------------------------
    audience_rows = []

    for i in range(counts["audience_segments"]):
        influencer = random.choice(influencer_records)

        age_min = random.choice([18, 25, 35, 45])
        age_max = min(
            65, age_min + random.choice([9, 14, 19])
        )

        selected_interests = random.sample(
            INTERESTS, k=int(rng.integers(1, 4))
        )

        audience_rows.append({
            "audience_segment_id": f"AU{i + 1:07d}",
            "influencer_id": influencer["influencer_id"],
            "age_min": age_min,
            "age_max": age_max,
            "gender": random.choice(
                ["Female", "Male", "Mixed"]
            ),
            "location": random.choice(LOCATIONS),
            "interests": json.dumps(selected_interests),
            "audience_share": round(
                float(rng.uniform(0.1, 0.8)), 4
            )
        })

    audience_df = pd.DataFrame(audience_rows)


    # ---------------------------------------------------------
    # 5. Brand affinity
    # ---------------------------------------------------------
    requested_affinities = counts["brand_affinity"]
    total_pairs = len(influencer_records) * len(brand_records)

    if requested_affinities > total_pairs:
        raise ValueError(
            "brand_affinity cannot exceed unique influencer-brand pairs"
        )

    # Sample unique influencer-brand pairs.
    pair_ids = rng.choice(
        total_pairs, size=requested_affinities, replace=False
    )

    affinity_rows = []

    for pair in pair_ids:
        influencer_idx = int(pair // len(brand_records))
        brand_idx = int(pair % len(brand_records))

        influencer = influencer_records[influencer_idx]
        brand = brand_records[brand_idx]

        category_match = (
            influencer["primary_niche"] == brand["primary_category"]
        )

        affinity_score = float(
            rng.uniform(65, 98) if category_match
            else rng.uniform(10, 75)
        )

        affinity_rows.append({
            "influencer_id": influencer["influencer_id"],
            "brand_id": brand["brand_id"],
            "category_match": category_match,
            "affinity_score": round(affinity_score, 2)
        })

    affinity_df = pd.DataFrame(affinity_rows)

    affinity_lookup = {
        (row["influencer_id"], row["brand_id"]):
            row["affinity_score"]
        for row in affinity_rows
    }

    # ---------------------------------------------------------
    # 6. Campaigns
    # ---------------------------------------------------------
    campaigns = []

    for i in range(counts["campaigns"]):
        product = random.choice(product_records)
        brand = brand_by_id[product["brand_id"]]

        age_min = max(
            brand["target_age_min"], int(rng.integers(18, 36))
        )
        age_max = min(
            65, max(age_min, brand["target_age_max"])
        )

        campaigns.append({
            "campaign_id": f"CA{i + 1:06d}",
            "brand_id": brand["brand_id"],
            "product_id": product["product_id"],
            "objective": random.choice(OBJECTIVES),
            "platform": random.choice(PLATFORMS),
            "target_category": product["category"],
            "target_age_min": age_min,
            "target_age_max": age_max,
            "target_location": random.choice(LOCATIONS),
            "target_interests": json.dumps(
                random.sample(INTERESTS, k=3)
            ),
            "budget": round(float(rng.uniform(1000, 100000)), 2)
        })

    campaigns_df = pd.DataFrame(campaigns)
    campaign_records = campaigns_df.to_dict("records")

    # ---------------------------------------------------------
    # 7. Campaign performance and synthetic relevance labels
    # ---------------------------------------------------------
    influencers_by_platform = {}

    for influencer in influencer_records:
        influencers_by_platform.setdefault(
            influencer["platform"], []
        ).append(influencer)

    performance_rows = []

    for i in range(counts["campaign_performance"]):
        campaign = random.choice(campaign_records)
        brand_id = campaign["brand_id"]

        eligible_pool = influencers_by_platform[campaign["platform"]]
        influencer = random.choice(eligible_pool)

        category_match = (
            influencer["primary_niche"] == campaign["target_category"]
        )

        affinity = affinity_lookup.get(
            (influencer["influencer_id"], brand_id), 50.0
        )

        target_interests = set(
            json.loads(campaign["target_interests"])
        )

        # This is a synthetic relevance signal, not real-world truth.
        interest_match = (
            campaign["target_category"].lower() in target_interests
            or category_match
        )

        relevance_score = (
            0.45 * (100 if category_match else 0)
            + 0.30 * affinity
            + 0.25 * (100 if interest_match else 0)
        )

        is_relevant = relevance_score >= 55

        impressions = max(
            100,
            int(influencer["follower_count"] * rng.uniform(0.15, 0.8))
        )

        reach = max(
            1,
            int(impressions * rng.uniform(0.55, 0.9))
        )

        engagement_rate = influencer["engagement_rate"]
        likes = int(impressions * engagement_rate * rng.uniform(0.6, 0.9))
        comments = int(impressions * engagement_rate * rng.uniform(0.03, 0.12))
        shares = int(impressions * engagement_rate * rng.uniform(0.02, 0.1))

        # Relevant matches have a modestly higher expected response.
        response_multiplier = 1.25 if is_relevant else 0.75
        clicks = int(
            impressions
            * rng.uniform(0.005, 0.03)
            * response_multiplier
        )
        conversions = int(
            clicks * rng.uniform(0.01, 0.12)
        )

        spend = round(
            min(
                campaign["budget"],
                influencer["average_rate"] * rng.uniform(0.8, 1.2)
            ),
            2
        )

        performance_rows.append({
            "performance_id": f"PF{i + 1:07d}",
            "campaign_id": campaign["campaign_id"],
            "influencer_id": influencer["influencer_id"],
            "impressions": impressions,
            "reach": reach,
            "likes": likes,
            "comments": comments,
            "shares": shares,
            "clicks": clicks,
            "conversions": conversions,
            "spend": spend,
            "revenue": round(
                conversions * rng.uniform(20, 150), 2
            ),
            "synthetic_relevance_score": round(relevance_score, 2),
            "is_relevant": bool(is_relevant)
        })

    performance_df = pd.DataFrame(performance_rows)

    datasets = {
        "influencers": influencers_df,
        "audience_segments": audience_df,
        "brands": brands_df,
        "products": products_df,
        "brand_affinity": affinity_df,
        "campaigns": campaigns_df,
        "campaign_performance": performance_df
    }

    validate_datasets(datasets)

    destination = (
        Path(output_dir) if output_dir
        else ROOT_DIR / config.get("output_dir", "data/synthetic")
    )
    destination.mkdir(parents=True, exist_ok=True)

    output_formats = formats or config.get(
        "formats", ["csv", "parquet"]
    )

    for name, dataframe in datasets.items():
        for fmt in output_formats:
            path = destination / f"{name}.{fmt}"

            if fmt == "csv":
                dataframe.to_csv(path, index=False)
            elif fmt == "parquet":
                dataframe.to_parquet(path, index=False)
            else:
                raise ValueError(f"Unsupported format: {fmt}")

    return datasets


def validate_datasets(datasets):
    """Raise ValueError if the generated datasets violate core rules."""

    for name, dataframe in datasets.items():
        if dataframe.empty:
            raise ValueError(f"{name} is empty")

        if dataframe.isnull().any().any():
            raise ValueError(f"{name} contains null values")

    influencers = datasets["influencers"]
    brands = datasets["brands"]
    products = datasets["products"]
    audiences = datasets["audience_segments"]
    affinities = datasets["brand_affinity"]
    campaigns = datasets["campaigns"]
    performance = datasets["campaign_performance"]

    if not influencers["influencer_id"].is_unique:
        raise ValueError("Duplicate influencer IDs")

    if not brands["brand_id"].is_unique:
        raise ValueError("Duplicate brand IDs")

    if not products["product_id"].is_unique:
        raise ValueError("Duplicate product IDs")

    if not campaigns["campaign_id"].is_unique:
        raise ValueError("Duplicate campaign IDs")

    if not performance["performance_id"].is_unique:
        raise ValueError("Duplicate performance IDs")

    influencer_ids = set(influencers["influencer_id"])
    brand_ids = set(brands["brand_id"])
    product_ids = set(products["product_id"])
    campaign_ids = set(campaigns["campaign_id"])

    if not set(products["brand_id"]).issubset(brand_ids):
        raise ValueError("Products reference unknown brands")

    if not set(audiences["influencer_id"]).issubset(influencer_ids):
        raise ValueError("Audience segments reference unknown influencers")

    if not set(affinities["influencer_id"]).issubset(influencer_ids):
        raise ValueError("Brand affinities reference unknown influencers")

    if not set(affinities["brand_id"]).issubset(brand_ids):
        raise ValueError("Brand affinities reference unknown brands")

    if not set(campaigns["brand_id"]).issubset(brand_ids):
        raise ValueError("Campaigns reference unknown brands")

    if not set(campaigns["product_id"]).issubset(product_ids):
        raise ValueError("Campaigns reference unknown products")

    if not set(performance["campaign_id"]).issubset(campaign_ids):
        raise ValueError("Performance records reference unknown campaigns")

    if not set(performance["influencer_id"]).issubset(influencer_ids):
        raise ValueError("Performance records reference unknown influencers")

    if not affinities["affinity_score"].between(0, 100).all():
        raise ValueError("Affinity scores must be between 0 and 100")

    if (influencers["follower_count"] <= 0).any():
        raise ValueError("Follower counts must be positive")

    if (campaigns["budget"] <= 0).any():
        raise ValueError("Campaign budgets must be positive")

    if (performance["reach"] > performance["impressions"]).any():
        raise ValueError("Reach cannot exceed impressions")


if __name__ == "__main__":
    generated = generate_datasets()

    print("\nSynthetic data generation completed.")
    print("-" * 55)

    for name, dataframe in generated.items():
        print(f"{name:25} {len(dataframe):>8,} records")

    print(f"\nOutput directory: {ROOT_DIR / 'data' / 'synthetic'}")
