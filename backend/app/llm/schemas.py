
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


Category = Literal[
    "Beauty",
    "Skincare",
    "Fashion",
    "Fitness",
    "Food",
    "Travel",
    "Technology",
    "Home",
    "Lifestyle",
    "Gaming",
]

Platform = Literal["Instagram", "YouTube", "TikTok"]

Objective = Literal[
    "Awareness",
    "Engagement",
    "Conversions",
    "Sales",
]


class CampaignBriefRequest(BaseModel):
    brief: str = Field(..., min_length=10, max_length=5000)


class CampaignCriteria(BaseModel):
    objective: Optional[Objective] = None
    platform: Optional[Platform] = None
    target_category: Optional[Category] = None
    target_age_min: Optional[int] = Field(default=None, ge=18, le=65)
    target_age_max: Optional[int] = Field(default=None, ge=18, le=65)
    target_location: Optional[str] = None
    target_interests: List[str] = Field(default_factory=list)
    budget: Optional[float] = Field(default=None, gt=0)


class CampaignInterpretation(BaseModel):
    criteria: CampaignCriteria
    missing_fields: List[str] = Field(default_factory=list)


class InfluencerEvidence(BaseModel):
    influencer_id: str
    platform: str
    primary_niche: str
    follower_count: int = Field(..., ge=0)
    engagement_rate: float = Field(..., ge=0)
    location: str
    average_rate: float = Field(..., ge=0)


class ScoreBreakdown(BaseModel):
    match_score: float = Field(..., ge=0, le=100)
    audience_fit: float = Field(..., ge=0, le=100)
    engagement_quality: float = Field(..., ge=0, le=100)
    brand_affinity: float = Field(..., ge=0, le=100)
    historical_performance: float = Field(..., ge=0, le=100)
    cost_effectiveness: float = Field(..., ge=0, le=100)
    estimated_cost: float = Field(..., ge=0)


class RecommendationExplanationRequest(BaseModel):
    campaign: CampaignCriteria
    influencer: InfluencerEvidence
    scores: ScoreBreakdown


class RecommendationExplanation(BaseModel):
    influencer_id: str
    summary: str
    strengths: List[str]
    considerations: List[str]
