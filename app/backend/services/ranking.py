from app.backend.models.schemas import ProductReview, Recommendation, UserProfileRequest
from app.backend.services.explain import build_recommendation_reason, get_concern_matches
from app.backend.services.filtering import calculate_ad_score


def build_sort_key(
    user_profile: UserProfileRequest,
    review: ProductReview,
    normalized_skin_type: str,
) -> tuple[int, int, float]:
    matched_concerns = get_concern_matches(user_profile, review)
    matched_skin_type = review.skin_type.strip().lower() == normalized_skin_type

    return (
        int(matched_skin_type),
        len(matched_concerns),
        review.rating,
    )


def rank_products(
    user_profile: UserProfileRequest,
    reviews: list[ProductReview],
    limit: int = 3,
) -> tuple[list[Recommendation], str]:
    normalized_skin_type = user_profile.skin_type.strip().lower()

    exact_matches = [
        review for review in reviews if review.skin_type.strip().lower() == normalized_skin_type
    ]
    non_matches = [
        review for review in reviews if review.skin_type.strip().lower() != normalized_skin_type
    ]

    exact_matches.sort(
        key=lambda review: build_sort_key(user_profile, review, normalized_skin_type),
        reverse=True,
    )
    non_matches.sort(
        key=lambda review: build_sort_key(user_profile, review, normalized_skin_type),
        reverse=True,
    )

    if exact_matches:
        ranked_reviews = (exact_matches + non_matches)[:limit]
        strategy = "exact_match_prioritized"
    else:
        ranked_reviews = sorted(
            reviews,
            key=lambda review: build_sort_key(user_profile, review, normalized_skin_type),
            reverse=True,
        )[:limit]
        strategy = "highest_rated_fallback"

    recommendations = [
        Recommendation(
            product=review.product,
            skin_type=review.skin_type,
            rating=review.rating,
            review=review.review,
            ad_score=calculate_ad_score(review),
            matched_skin_type=review.skin_type.strip().lower() == normalized_skin_type,
            reason=build_recommendation_reason(user_profile, review),
        )
        for review in ranked_reviews
    ]

    return recommendations, strategy
