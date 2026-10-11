from pathlib import Path
from typing import List, Optional

import pandas as pd
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, validator

from backend.app.matching.engine import InfluencerMatchingEngine
from backend.app.llm.schemas import CampaignCriteria, InfluencerEvidence, ScoreBreakdown
from backend.app.llm.service import LLMService

router = APIRouter(prefix="/api/matching", tags=["Influencer Matching"])
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"


def _read_dataset(name: str) -> pd.DataFrame:
    parquet_path = DATA_DIR / "{}.parquet".format(name)
    csv_path = DATA_DIR / "{}.csv".format(name)
    try:
        if parquet_path.exists():
            return pd.read_parquet(parquet_path)
        if csv_path.exists():
            return pd.read_csv(csv_path)
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Could not read dataset '{}': {}".format(name, exc)) from exc
    raise HTTPException(status_code=404, detail="Dataset '{}' was not found under {}".format(name, DATA_DIR))


class MatchRequest(BaseModel):
    brand_id: str = Field(..., min_length=1)
    criteria: CampaignCriteria
    top_k: int = Field(10, ge=1, le=100)


class ExplanationRequest(BaseModel):
    campaign: CampaignCriteria
    influencer_id: str
    scores: dict


@router.get("/brands")
def list_brands():
    brands = _read_dataset("brands")
    required = {"brand_id", "brand_name", "primary_category"}
    if not required.issubset(brands.columns):
        raise HTTPException(status_code=500, detail="Brands dataset is missing required columns.")
    return {"brands": brands[["brand_id", "brand_name", "primary_category"]].sort_values("brand_name").to_dict("records")}


@router.post("/recommendations")
def get_recommendations(request: MatchRequest):
    criteria = request.criteria
    required = {
        "platform": criteria.platform,
        "target_category": criteria.target_category,
        "target_age_min": criteria.target_age_min,
        "target_age_max": criteria.target_age_max,
        "target_location": criteria.target_location,
        "budget": criteria.budget,
    }
    missing = [name for name, value in required.items() if value is None or value == ""]
    if missing:
        raise HTTPException(
            status_code=422,
            detail="Campaign criteria are incomplete. Re-submit a brief that specifies: {}.".format(", ".join(missing)),
        )
    if criteria.target_age_min > criteria.target_age_max:
        raise HTTPException(status_code=422, detail="target_age_min must not exceed target_age_max.")

    try:
        brands = _read_dataset("brands")
        if request.brand_id not in set(brands["brand_id"].astype(str)):
            raise HTTPException(status_code=422, detail="Select a valid brand.")
        influencers = _read_dataset("influencers")
        audiences = _read_dataset("audience_segments")
        affinities = _read_dataset("brand_affinity")
        performance = _read_dataset("campaign_performance")

        campaign = {
            "campaign_id": "LIVE_REQUEST",
            "brand_id": request.brand_id,
            "platform": criteria.platform,
            "target_category": criteria.target_category,
            "target_age_min": criteria.target_age_min,
            "target_age_max": criteria.target_age_max,
            "target_location": criteria.target_location,
            "target_interests": criteria.target_interests,
            "budget": criteria.budget,
        }
        engine = InfluencerMatchingEngine()
        ranked = engine.match(campaign, influencers, audiences, affinities, performance)
        ranked = ranked.head(request.top_k)
        if ranked.empty:
            return {"brand_id": request.brand_id, "count": 0, "results": [], "ranking_method": "weighted_baseline"}

        # Add profile evidence from the source dataset; do not fabricate scores.
        profile_cols = ["influencer_id", "display_name", "verified"]
        available = [c for c in profile_cols if c in influencers.columns]
        if available:
            ranked = ranked.merge(influencers[available].drop_duplicates("influencer_id"), on="influencer_id", how="left")
        results = []
        for row in ranked.to_dict("records"):
            for key, value in list(row.items()):
                if hasattr(value, "item"):
                    row[key] = value.item()
                elif pd.isna(value):
                    row[key] = None
            row["score_breakdown"] = {
                key: row.get(key)
                for key in ["audience_fit", "engagement_quality", "brand_affinity", "historical_performance", "cost_effectiveness"]
            }
            results.append(row)
        return {
            "brand_id": request.brand_id,
            "count": len(results),
            "results": results,
            "ranking_method": "weighted_baseline",
            "weights": engine.weights,
            "note": "Scores are generated from synthetic data and the configured weighted matching rules."
        }
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Matching failed. Check backend logs: {}".format(exc)) from exc


@router.post("/explain")
def explain_recommendation(request: ExplanationRequest):
    criteria = request.campaign
    required = [criteria.platform, criteria.target_category, criteria.budget]
    if any(value is None for value in required):
        raise HTTPException(status_code=422, detail="Campaign platform, category and budget are required for an explanation.")
    try:
        influencers = _read_dataset("influencers")
        matches = influencers[influencers["influencer_id"].astype(str) == request.influencer_id]
        if matches.empty:
            raise HTTPException(status_code=404, detail="Influencer was not found.")
        row = matches.iloc[0]
        influencer = InfluencerEvidence(
            influencer_id=str(row["influencer_id"]),
            platform=str(row["platform"]),
            primary_niche=str(row["primary_niche"]),
            follower_count=int(row["follower_count"]),
            engagement_rate=float(row["engagement_rate"]),
            location=str(row["location"]),
            average_rate=float(row["average_rate"]),
        )
        score_values = request.scores
        score_model = ScoreBreakdown(
            match_score=score_values.get("match_score", 0),
            audience_fit=score_values.get("audience_fit", 0),
            engagement_quality=score_values.get("engagement_quality", 0),
            brand_affinity=score_values.get("brand_affinity", 0),
            historical_performance=score_values.get("historical_performance", 0),
            cost_effectiveness=score_values.get("cost_effectiveness", 0),
            estimated_cost=score_values.get("estimated_cost", float(row["average_rate"])),
        )
        service = LLMService()
        result = service.explain_recommendation(
            campaign=criteria.dict(),
            influencer=influencer.dict(),
            scores=score_model.dict(),
        )
        return result.dict() if hasattr(result, "dict") else result
    except HTTPException:
        raise
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail="LLM service is not configured. Check backend/.env.") from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail="Recommendation explanation failed. Check backend logs.") from exc
