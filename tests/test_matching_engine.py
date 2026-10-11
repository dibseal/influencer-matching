
import json

import pandas as pd
import pytest

from backend.app.matching.engine import InfluencerMatchingEngine


@pytest.fixture
def engine(tmp_path):
    config = {
        "weights": {
            "audience_fit": 0.30,
            "engagement_quality": 0.20,
            "brand_affinity": 0.20,
            "historical_performance": 0.20,
            "cost_effectiveness": 0.10,
        },
        "minimum_followers": 1000,
        "maximum_budget_utilization": 1.0,
    }

    path = tmp_path / "matching_config.json"
    path.write_text(json.dumps(config), encoding="utf-8")

    return InfluencerMatchingEngine(path)


@pytest.fixture
def sample_data():
    campaign = {
        "campaign_id": "CA001",
        "brand_id": "BR001",
        "platform": "Instagram",
        "target_category": "Beauty",
        "target_age_min": 25,
        "target_age_max": 40,
        "target_location": "India",
        "target_interests": json.dumps(["skincare", "beauty"]),
        "budget": 5000,
    }

    influencers = pd.DataFrame([
        {
            "influencer_id": "IN001",
            "platform": "Instagram",
            "primary_niche": "Beauty",
            "follower_count": 10000,
            "engagement_rate": 0.06,
            "location": "India",
            "average_rate": 1000,
        },
        {
            "influencer_id": "IN002",
            "platform": "YouTube",
            "primary_niche": "Technology",
            "follower_count": 50000,
            "engagement_rate": 0.03,
            "location": "India",
            "average_rate": 2000,
        },
        {
            "influencer_id": "IN003",
            "platform": "Instagram",
            "primary_niche": "Beauty",
            "follower_count": 5000,
            "engagement_rate": 0.04,
            "location": "India",
            "average_rate": 10000,
        },
    ])

    audiences = pd.DataFrame([
        {
            "influencer_id": "IN001",
            "age_min": 25,
            "age_max": 40,
            "location": "India",
            "interests": '["skincare", "beauty"]',
        },
        {
            "influencer_id": "IN002",
            "age_min": 25,
            "age_max": 40,
            "location": "India",
            "interests": '["technology"]',
        },
        {
            "influencer_id": "IN003",
            "age_min": 25,
            "age_max": 40,
            "location": "India",
            "interests": '["beauty"]',
        },
    ])

    affinity = pd.DataFrame([
        {
            "influencer_id": "IN001",
            "brand_id": "BR001",
            "affinity_score": 95,
        },
        {
            "influencer_id": "IN003",
            "brand_id": "BR001",
            "affinity_score": 80,
        },
    ])

    performance = pd.DataFrame([
        {
            "campaign_id": "OLD001",
            "influencer_id": "IN001",
            "impressions": 10000,
            "likes": 500,
            "comments": 100,
            "shares": 50,
            "clicks": 300,
            "conversions": 30,
            "revenue": 6000,
            "spend": 1000,
        }
    ])

    return (
        campaign, influencers, audiences, affinity, performance
    )


def test_returns_eligible_influencers(engine, sample_data):
    results = engine.match(*sample_data)

    assert set(results["influencer_id"]) == {"IN001"}
    assert "IN002" not in set(results["influencer_id"])
    assert "IN003" not in set(results["influencer_id"])


def test_score_is_bounded(engine, sample_data):
    campaign, influencers, audiences, affinity, performance = sample_data

    influencers = influencers.iloc[[0]].copy()
    audiences = audiences[audiences["influencer_id"] == "IN001"]

    results = engine.match(
        campaign, influencers, audiences, affinity, performance
    )

    assert results["match_score"].between(0, 100).all()


def test_invalid_budget_is_rejected(engine, sample_data):
    campaign, influencers, audiences, affinity, performance = sample_data
    campaign = {**campaign, "budget": 0}

    with pytest.raises(ValueError, match="budget"):
        engine.match(
            campaign, influencers, audiences, affinity, performance
        )


def test_empty_eligible_pool_returns_empty_results(engine, sample_data):
    campaign, influencers, audiences, affinity, performance = sample_data
    campaign = {**campaign, "platform": "TikTok"}

    results = engine.match(
        campaign, influencers, audiences, affinity, performance
    )

    assert results.empty


def test_results_are_ranked_descending(engine, sample_data):
    campaign, influencers, audiences, affinity, performance = sample_data

    influencers = influencers.iloc[[0]].copy()
    audiences = audiences[audiences["influencer_id"] == "IN001"]

    results = engine.match(
        campaign, influencers, audiences, affinity, performance
    )

    assert results["match_score"].is_monotonic_decreasing
