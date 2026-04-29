import logging

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.backend.database import get_session
from app.backend.db_models import ReviewRecord
from app.backend.models.schemas import (
    ReviewSubmissionRequest,
    ReviewSubmissionResponse,
    UserProfileRequest,
    UserProfileResponse,
)
from app.backend.services.decision_agent import decision_agent
from app.backend.services.review_processing import process_review_submission


router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/profile", response_model=UserProfileResponse)
async def create_user_profile(
    payload: UserProfileRequest,
    db: Session = Depends(get_session),
) -> UserProfileResponse:
    logger.info("Incoming user profile: %s", payload.model_dump())
    response = decision_agent(payload, db)

    logger.info(
        "Decision agent summary: category=%s total=%s filtered=%s trust_score=%s confidence=%s",
        payload.category,
        response.total_reviews_analyzed,
        response.filtered_reviews_count,
        response.trust_score,
        response.final_decision.confidence_score,
    )
    logger.info(
        "Selected recommendations: %s",
        [recommendation.model_dump() for recommendation in response.recommendations],
    )

    return response


@router.post("/review", response_model=ReviewSubmissionResponse)
async def create_review(
    payload: ReviewSubmissionRequest,
    db: Session = Depends(get_session),
) -> ReviewSubmissionResponse:
    keywords, is_ad = process_review_submission(payload)

    review_record = ReviewRecord(
        product_name="user_submitted",
        brand_name=payload.brand_name,
        category=payload.category,
        review_text=payload.review_text,
        skin_type=payload.skin_type,
        rating=payload.rating,
        keywords=keywords,
        is_ad=is_ad,
    )
    db.add(review_record)
    db.commit()

    logger.info(
        "Stored user review: %s",
        {
            "brand_name": payload.brand_name,
            "category": payload.category,
            "skin_type": payload.skin_type,
            "rating": payload.rating,
            "keywords": keywords,
            "is_ad": is_ad,
        },
    )

    return ReviewSubmissionResponse(
        success=True,
        message="Review submitted successfully.",
        keywords=keywords,
        is_ad=is_ad,
    )
