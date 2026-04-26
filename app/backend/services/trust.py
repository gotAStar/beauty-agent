from statistics import pstdev

from app.backend.models.schemas import ProductReview


VALID_REVIEW_WEIGHT = 40
AD_FILTER_WEIGHT = 35
CONSISTENCY_WEIGHT = 25
VALID_REVIEW_TARGET = 5
MAX_RATING_STD_DEV = 1.5


def calculate_trust_score(
    valid_reviews: list[ProductReview],
    filtered_reviews_count: int,
    total_reviews_analyzed: int,
) -> int:
    if total_reviews_analyzed <= 0:
        return 0

    valid_review_ratio = min(len(valid_reviews) / VALID_REVIEW_TARGET, 1.0)
    valid_review_score = valid_review_ratio * VALID_REVIEW_WEIGHT

    filtered_ratio = filtered_reviews_count / total_reviews_analyzed
    ad_filter_score = (1 - filtered_ratio) * AD_FILTER_WEIGHT

    ratings = [review.rating for review in valid_reviews]
    if not ratings:
        consistency_ratio = 0.0
    elif len(ratings) == 1:
        consistency_ratio = 0.5
    else:
        consistency_ratio = max(0.0, 1 - (pstdev(ratings) / MAX_RATING_STD_DEV))

    consistency_score = consistency_ratio * CONSISTENCY_WEIGHT

    return round(valid_review_score + ad_filter_score + consistency_score)
