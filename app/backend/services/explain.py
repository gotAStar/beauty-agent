from app.backend.models.schemas import ProductReview, UserProfileRequest


CONCERN_KEYWORDS = {
    "dryness": ["hydrating", "hydrate", "moisturizing", "moisturizer", "moisture"],
    "acne": ["acne", "reduce acne", "breakouts", "breakout", "blemishes"],
    "oily": ["oil", "oily", "oil control", "shine", "greasy", "balance"],
    "redness": ["redness", "calming", "soothing", "gentle"],
    "texture": ["smooth", "smoother", "texture", "refine", "soft"],
    "dark-spots": ["dark spots", "brightening", "even tone", "fade marks"],
}


def get_normalized_concerns(user_profile: UserProfileRequest) -> list[str]:
    return [concern.strip().lower() for concern in user_profile.concerns if concern.strip()]


def get_concern_keyword_hits(
    user_profile: UserProfileRequest,
    review: ProductReview,
) -> dict[str, list[str]]:
    normalized_review = review.review.strip().lower()
    concern_hits: dict[str, list[str]] = {}

    for concern in get_normalized_concerns(user_profile):
        keywords = CONCERN_KEYWORDS.get(concern, [])
        matched_keywords = [keyword for keyword in keywords if keyword in normalized_review]

        if matched_keywords:
            concern_hits[concern] = matched_keywords

    return concern_hits


def get_concern_matches(user_profile: UserProfileRequest, review: ProductReview) -> list[str]:
    return list(get_concern_keyword_hits(user_profile, review).keys())


def build_recommendation_reason(
    user_profile: UserProfileRequest,
    review: ProductReview,
    supporting_reviews_count: int,
    average_rating: float,
    concern_hits: dict[str, list[str]],
    total_keyword_hits: int,
    ad_score: float,
    score_breakdown: dict[str, float],
) -> str:
    normalized_skin_type = user_profile.skin_type.strip().lower()
    matched_skin_type = review.skin_type.strip().lower() == normalized_skin_type

    positive_signals: list[str] = []
    negative_signals: list[str] = []

    if matched_skin_type:
        positive_signals.append(f"matches your skin type ({user_profile.skin_type})")
    else:
        negative_signals.append(
            f"product is labeled for {review.skin_type} skin, not {user_profile.skin_type}"
        )

    for concern, keywords in concern_hits.items():
        positive_signals.append(
            f"mentions {concern} support with keywords like \"{keywords[0]}\""
        )

    if user_profile.concerns and not concern_hits:
        negative_signals.append("review does not clearly mention your selected concerns")

    if total_keyword_hits > 0:
        positive_signals.append(
            f"contains {total_keyword_hits} concern-related keyword hits across {supporting_reviews_count} valid review(s)"
        )

    if supporting_reviews_count > 1:
        positive_signals.append(f"supported by {supporting_reviews_count} valid reviews")
    else:
        negative_signals.append("only one supporting valid review")

    if average_rating >= 4.5:
        positive_signals.append(f"strong average rating ({average_rating:.1f}/5)")
    elif average_rating >= 4.0:
        positive_signals.append(f"solid average rating ({average_rating:.1f}/5)")
    else:
        negative_signals.append(f"weaker average rating ({average_rating:.1f}/5)")

    if ad_score > 0:
        negative_signals.append(f"minor promotional language risk (ad score {ad_score:.2f})")

    if not positive_signals:
        positive_signals.append("limited direct evidence beyond passing the review quality filter")

    if not negative_signals:
        negative_signals.append("limited downside signals in the short review text")

    return (
        f'Review says: "{review.review}". '
        f'Positive signals: {"; ".join(positive_signals)}. '
        f'Negative signals: {"; ".join(negative_signals)}. '
        f'Score breakdown: skin {score_breakdown["skin_type"]:.1f}, '
        f'concern coverage {score_breakdown["concern_coverage"]:.1f}, '
        f'keyword frequency {score_breakdown["keyword_frequency"]:.1f}, '
        f'rating {score_breakdown["rating"]:.1f}, '
        f'review support {score_breakdown["supporting_reviews"]:.1f}, '
        f'ad penalty -{score_breakdown["ad_penalty"]:.1f}.'
    )
