
import logging

from fastapi import APIRouter, HTTPException

from backend.app.llm.schemas import (
    CampaignBriefRequest,
    CampaignInterpretation,
    RecommendationExplanationRequest,
    RecommendationExplanation,
)
from backend.app.llm.service import LLMService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/llm",
    tags=["LLM Services"],
)


def to_dict(model):
    if hasattr(model, "model_dump"):
        return model.model_dump()

    return model.dict()


def get_service():
    try:
        return LLMService()
    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="LLM service is not configured. Check backend/.env.",
        ) from exc


@router.post(
    "/interpret-campaign",
    response_model=CampaignInterpretation,
)
def interpret_campaign(request: CampaignBriefRequest):
    service = get_service()

    try:
        return service.interpret_campaign(request.brief)
    except Exception as exc:
        logger.exception("Campaign interpretation failed")
        raise HTTPException(
            status_code=502,
            detail="Campaign interpretation failed. Check the backend logs.",
        ) from exc


@router.post(
    "/explain-recommendation",
    response_model=RecommendationExplanation,
)
def explain_recommendation(
    request: RecommendationExplanationRequest,
):
    service = get_service()

    try:
        return service.explain_recommendation(
            campaign=to_dict(request.campaign),
            influencer=to_dict(request.influencer),
            scores=to_dict(request.scores),
        )
    except Exception as exc:
        logger.exception("Recommendation explanation failed")
        raise HTTPException(
            status_code=502,
            detail="Recommendation explanation failed. Check the backend logs.",
        ) from exc
