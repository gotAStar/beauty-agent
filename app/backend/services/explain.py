from app.backend.models.schemas import ProductReview, UserProfileRequest


CONCERN_KEYWORDS = {
    "dryness": ["hydrating", "hydrate", "moisturizing", "moisturizer", "moisture"],
    "acne": ["acne", "reduce acne", "breakouts", "breakout", "blemishes"],
    "redness": ["redness", "calming", "soothing", "gentle"],
    "texture": ["smooth", "smoother", "texture", "refine", "soft"],
    "dark-spots": ["dark spots", "brightening", "even tone", "fade marks"],
}


def get_concern_keyword_hits(
    user_profile: UserProfileRequest,
    review: ProductReview,
) -> dict[str, list[str]]:
    normalized_review = review.review.strip().lower()
    concern_hits: dict[str, list[str]] = {}

    for concern in user_profile.concerns:
        normalized_concern = concern.strip().lower()
        keywords = CONCERN_KEYWORDS.get(normalized_concern, [])
        matched_keywords = [keyword for keyword in keywords if keyword in normalized_review]

        if matched_keywords:
            concern_hits[normalized_concern] = matched_keywords

    return concern_hits


def get_concern_matches(user_profile: UserProfileRequest, review: ProductReview) -> list[str]:
    return list(get_concern_keyword_hits(user_profile, review).keys())


def build_recommendation_reason(
    user_profile: UserProfileRequest,
    review: ProductReview,
) -> str:
    normalized_skin_type = user_profile.skin_type.strip().lower()
    matched_skin_type = review.skin_type.strip().lower() == normalized_skin_type
    concern_hits = get_concern_keyword_hits(user_profile, review)

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

    if review.rating >= 4.5:
        positive_signals.append(f"strong rating ({review.rating:.1f}/5)")
    elif matched_skin_type or concern_hits:
        negative_signals.append(f"more moderate rating ({review.rating:.1f}/5)")

    if not positive_signals:
        positive_signals.append("limited direct evidence beyond passing the review quality filter")

    if not negative_signals:
        negative_signals.append("limited downside signals in the short review text")

    return (
        f'Review says: "{review.review}". '
        f'Positive signals: {"; ".join(positive_signals)}. '
        f'Negative signals: {"; ".join(negative_signals)}.'
    )
