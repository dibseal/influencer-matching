
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_CONFIG = ROOT_DIR / "config" / "matching_config.json"


class InfluencerMatchingEngine:
    def __init__(self, config_path=None):
        path = Path(config_path) if config_path else DEFAULT_CONFIG

        with path.open("r", encoding="utf-8") as file:
            self.config = json.load(file)

        self.weights = self.config["weights"]

        required_weights = {
            "audience_fit",
            "engagement_quality",
            "brand_affinity",
            "historical_performance",
            "cost_effectiveness",
        }

        if set(self.weights) != required_weights:
            raise ValueError("Invalid matching weight configuration")

        if not np.isclose(sum(self.weights.values()), 1.0):
            raise ValueError("Matching weights must sum to 1.0")

        if any(
            not isinstance(weight, (int, float))
            or not np.isfinite(weight)
            or weight < 0
            for weight in self.weights.values()
        ):
            raise ValueError("Weights must be finite and non-negative")

        self.minimum_followers = int(
            self.config.get("minimum_followers", 1000)
        )
        self.maximum_budget_utilization = float(
            self.config.get("maximum_budget_utilization", 1.0)
        )

        if self.minimum_followers < 0:
            raise ValueError("minimum_followers cannot be negative")

        if not 0 < self.maximum_budget_utilization <= 1:
            raise ValueError(
                "maximum_budget_utilization must be in (0, 1]"
            )

    @staticmethod
    def _parse_interests(value):
        if isinstance(value, list):
            return {str(item).strip().lower() for item in value}

        if isinstance(value, str):
            try:
                parsed = json.loads(value)
                if isinstance(parsed, list):
                    return {
                        str(item).strip().lower() for item in parsed
                    }
            except json.JSONDecodeError:
                pass

            return {
                item.strip().lower()
                for item in value.split(",")
                if item.strip()
            }

        return set()

    @staticmethod
    def _normalize(values):
        values = pd.to_numeric(values, errors="coerce")
        return values.clip(0, 100).fillna(0)

    def match(
        self,
        campaign,
        influencers,
        audiences,
        brand_affinity,
        campaign_performance,
    ):
        """Return eligible influencers ranked by match score.

        campaign: one campaign dictionary or pandas Series.
        Other inputs: pandas DataFrames.
        """
        campaign = dict(campaign)

        required_campaign_fields = {
            "brand_id",
            "platform",
            "target_category",
            "target_age_min",
            "target_age_max",
            "target_location",
            "target_interests",
            "budget",
        }

        missing = required_campaign_fields - set(campaign)
        if missing:
            raise ValueError(
                f"Missing campaign fields: {sorted(missing)}"
            )

        if not np.isfinite(float(campaign["budget"])) or campaign["budget"] <= 0:
            raise ValueError("Campaign budget must be positive and finite")

        if campaign["target_age_min"] > campaign["target_age_max"]:
            raise ValueError("Invalid target age range")

        required_columns = {
            "influencers": {
                "influencer_id", "platform", "primary_niche",
                "follower_count", "engagement_rate", "location",
                "average_rate",
            },
            "audiences": {
                "influencer_id", "age_min", "age_max",
                "location", "interests",
            },
            "brand_affinity": {
                "influencer_id", "brand_id", "affinity_score",
            },
            "campaign_performance": {
                "influencer_id", "campaign_id", "impressions",
                "likes", "comments", "shares", "clicks",
                "conversions", "revenue", "spend",
            },
        }

        supplied = {
            "influencers": influencers,
            "audiences": audiences,
            "brand_affinity": brand_affinity,
            "campaign_performance": campaign_performance,
        }

        for name, columns in required_columns.items():
            missing_columns = columns - set(supplied[name].columns)
            if missing_columns:
                raise ValueError(
                    f"{name} is missing columns: {sorted(missing_columns)}"
                )

        if influencers["influencer_id"].duplicated().any():
            raise ValueError("Influencer IDs must be unique")

        # -----------------------------------------------------
        # 1. Deterministic eligibility filtering
        # -----------------------------------------------------
        eligible = influencers.copy()

        eligible = eligible[
            eligible["platform"].str.casefold()
            == str(campaign["platform"]).casefold()
        ]

        eligible = eligible[
            eligible["follower_count"] >= self.minimum_followers
        ]

        eligible = eligible[
            eligible["average_rate"] <= (
                float(campaign["budget"])
                * self.maximum_budget_utilization
            )
        ]

        if eligible.empty:
            return pd.DataFrame(
                columns=[
                    "influencer_id", "match_score", "audience_fit",
                    "engagement_quality", "brand_affinity",
                    "historical_performance", "cost_effectiveness",
                    "estimated_cost",
                ]
            )

        # -----------------------------------------------------
        # 2. Audience fit
        # -----------------------------------------------------
        target_interests = self._parse_interests(
            campaign["target_interests"]
        )
        target_location = str(campaign["target_location"]).casefold()
        target_category = str(campaign["target_category"]).casefold()

        audience_fit = {}

        for influencer_id in eligible["influencer_id"]:
            rows = audiences[
                audiences["influencer_id"] == influencer_id
            ]

            scores = []

            for _, row in rows.iterrows():
                overlap_start = max(
                    float(row["age_min"]),
                    float(campaign["target_age_min"]),
                )
                overlap_end = min(
                    float(row["age_max"]),
                    float(campaign["target_age_max"]),
                )
                target_width = (
                    float(campaign["target_age_max"])
                    - float(campaign["target_age_min"]) + 1
                )
                age_score = max(
                    0, overlap_end - overlap_start + 1
                ) / target_width * 100

                interests = self._parse_interests(row["interests"])
                interest_score = (
                    len(interests & target_interests)
                    / max(1, len(target_interests)) * 100
                )

                location_score = (
                    100
                    if str(row["location"]).casefold() == target_location
                    else 0
                )

                scores.append(
                    0.50 * age_score
                    + 0.30 * interest_score
                    + 0.20 * location_score
                )

            audience_fit[influencer_id] = (
                float(np.mean(scores)) if scores else 0.0
            )

        # -----------------------------------------------------
        # 3. Engagement quality
        # -----------------------------------------------------
        ranked = eligible.copy()

        ranked["engagement_quality"] = self._normalize(
            ranked["engagement_rate"] * 1000
        )

        # -----------------------------------------------------
        # 4. Brand affinity
        # -----------------------------------------------------
        affinity = brand_affinity[
            brand_affinity["brand_id"] == campaign["brand_id"]
        ][["influencer_id", "affinity_score"]].copy()

        if affinity["influencer_id"].duplicated().any():
            raise ValueError(
                "Brand affinity must have at most one row per "
                "influencer and brand"
            )

        ranked = ranked.merge(
            affinity, on="influencer_id", how="left"
        )

        ranked["brand_affinity"] = (
            pd.to_numeric(ranked["affinity_score"], errors="coerce")
            .fillna(50)
            .clip(0, 100)
        )

        # -----------------------------------------------------
        # 5. Historical campaign performance
        # -----------------------------------------------------
        history = campaign_performance[
            campaign_performance["campaign_id"]
            != campaign.get("campaign_id")
        ].copy()

        if not history.empty:
            history["historical_score"] = (
                0.50 * self._normalize(
                    history["conversions"]
                    / history["clicks"].replace(0, np.nan) * 100
                )
                + 0.30 * self._normalize(
                    history["clicks"]
                    / history["impressions"].replace(0, np.nan) * 100
                )
                + 0.20 * self._normalize(
                    history["revenue"]
                    / history["spend"].replace(0, np.nan) * 25
                )
            )

            history_scores = history.groupby(
                "influencer_id"
            )["historical_score"].mean()

            ranked["historical_performance"] = (
                ranked["influencer_id"]
                .map(history_scores)
                .fillna(50)
                .clip(0, 100)
            )
        else:
            ranked["historical_performance"] = 50.0

        # -----------------------------------------------------
        # 6. Cost effectiveness
        # -----------------------------------------------------
        ranked["estimated_cost"] = ranked["average_rate"].astype(float)

        ranked["cost_effectiveness"] = (
            100 * (
                1 - ranked["estimated_cost"]
                / float(campaign["budget"])
            )
        ).clip(0, 100)

        # -----------------------------------------------------
        # 7. Weighted final score
        # -----------------------------------------------------
        ranked["audience_fit"] = (
            ranked["influencer_id"].map(audience_fit).fillna(0)
        )

        ranked["match_score"] = sum(
            ranked[feature] * weight
            for feature, weight in self.weights.items()
        ).round(2)

        ranked["match_score"] = ranked["match_score"].clip(0, 100)

        ranked = ranked.sort_values(
            ["match_score", "follower_count"],
            ascending=[False, False],
        ).reset_index(drop=True)

        return ranked[
            [
                "influencer_id",
                "match_score",
                "audience_fit",
                "engagement_quality",
                "brand_affinity",
                "historical_performance",
                "cost_effectiveness",
                "estimated_cost",
                "follower_count",
                "platform",
                "primary_niche",
                "location",
            ]
        ]
