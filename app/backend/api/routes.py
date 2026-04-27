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
from app.backend.services.filtering import filter_reviews
from app.backend.services.ingestion import load_reviews
from app.backend.services.ranking import rank_products
from app.backend.services.review_processing import process_review_submission
from app.backend.services.trust import calculate_trust_score


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

    reviews = load_reviews(db)
    category_reviews = reviews
    if payload.category != "all":
        matching_category_reviews = [
            review for review in reviews if review.category.strip().lower() == payload.category.strip().lower()
        ]
        if matching_category_reviews:
            category_reviews = matching_category_reviews

    filtered_reviews, filtered_reviews_count = filter_reviews(category_reviews)
    recommendations, strategy = rank_products(payload, filtered_reviews)
    trust_score = calculate_trust_score(
        filtered_reviews,
        filtered_reviews_count,
        len(category_reviews),
    )
    logger.info(
        "Review filtering summary: category=%s total=%s filtered=%s trust_score=%s",
        payload.category,
        len(category_reviews),
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
        total_reviews_analyzed=len(category_reviews),
        trust_score=trust_score,
    )


@router.post("/review", response_model=ReviewSubmissionResponse)
async def create_review(
    payload: ReviewSubmissionRequest,
    db: Session = Depends(get_session),
) -> ReviewSubmissionResponse:
    keywords, is_ad = process_review_submission(payload)

    review_record = ReviewRecord(
        product_name="user_submitted",
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
