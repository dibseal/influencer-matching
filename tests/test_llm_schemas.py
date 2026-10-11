
import pytest
from pydantic import ValidationError

from backend.app.llm.schemas import (
    CampaignBriefRequest,
    CampaignCriteria,
    ScoreBreakdown,
)


def test_campaign_brief_accepts_valid_input():
    request = CampaignBriefRequest(
        brief="Promote skincare products to adults in India."
    )

    assert "skincare" in request.brief


def test_campaign_brief_rejects_short_input():
    with pytest.raises(ValidationError):
        CampaignBriefRequest(brief="Hi")


def test_campaign_criteria_allows_missing_fields():
    criteria = CampaignCriteria(
        target_category="Skincare",
        target_interests=["skincare"],
    )

    assert criteria.budget is None
    assert criteria.platform is None


def test_campaign_criteria_rejects_invalid_category():
    with pytest.raises(ValidationError):
        CampaignCriteria(target_category="Automotive")


def test_score_breakdown_rejects_invalid_score():
    with pytest.raises(ValidationError):
        ScoreBreakdown(
            match_score=120,
            audience_fit=80,
            engagement_quality=80,
            brand_affinity=80,
            historical_performance=80,
            cost_effectiveness=80,
            estimated_cost=1000,
        )
