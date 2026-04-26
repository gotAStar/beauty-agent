import logging

from fastapi import APIRouter

from app.backend.models.schemas import UserProfileRequest, UserProfileResponse
from app.backend.services.filtering import filter_reviews
from app.backend.services.ingestion import load_reviews
from app.backend.services.ranking import rank_products
from app.backend.services.trust import calculate_trust_score


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    payload: UserProfileRequest,
) -> UserProfileResponse:
    logger.info("Incoming user profile: %s", payload.model_dump())

    reviews = load_reviews()
    filtered_reviews, filtered_reviews_count = filter_reviews(reviews)
    recommendations, strategy = rank_products(payload, filtered_reviews)
    trust_score = calculate_trust_score(
        filtered_reviews,
        filtered_reviews_count,
        len(reviews),
    )
    logger.info(
        "Review filtering summary: total=%s filtered=%s trust_score=%s",
        len(reviews),
        filtered_reviews_count,
        trust_score,
    )
    logger.info(
        "Selected recommendations: %s",
        [recommendation.model_dump() for recommendation in recommendations],
    )

    return UserProfileResponse(
        user_profile=payload,
        recommendations=recommendations,
        match_strategy=strategy,
        filtered_reviews_count=filtered_reviews_count,
        total_reviews_analyzed=len(reviews),
        trust_score=trust_score,
    )
