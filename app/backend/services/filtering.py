from app.backend.models.schemas import ProductReview


PROMOTIONAL_PHRASES = [
    "amazing",
    "must buy",
    "link in bio",
    "best ever",
]
AD_SCORE_THRESHOLD = 0.5


def calculate_ad_score(review: ProductReview) -> float:
    normalized_review = review.review.strip().lower()
    matches = sum(1 for phrase in PROMOTIONAL_PHRASES if phrase in normalized_review)

    return min(1.0, matches / len(PROMOTIONAL_PHRASES))


def filter_reviews(
    reviews: list[ProductReview],
    threshold: float = AD_SCORE_THRESHOLD,
) -> tuple[list[ProductReview], int]:
    filtered_reviews: list[ProductReview] = []
    removed_count = 0

    for review in reviews:
        ad_score = calculate_ad_score(review)

        if ad_score >= threshold:
            removed_count += 1
            continue

        filtered_reviews.append(review)

    return filtered_reviews, removed_count
