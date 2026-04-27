from collections import Counter, defaultdict
from dataclasses import dataclass
from statistics import mean

from app.backend.models.schemas import ProductReview, Recommendation, UserProfileRequest
from app.backend.services.explain import (
    CONCERN_KEYWORDS,
    build_recommendation_reason,
    get_concern_keyword_hits,
    get_normalized_concerns,
)
from app.backend.services.filtering import calculate_ad_score


SKIN_TYPE_WEIGHT = 30
CONCERN_COVERAGE_WEIGHT = 25
KEYWORD_FREQUENCY_WEIGHT = 15
RATING_WEIGHT = 20
SUPPORTING_REVIEWS_WEIGHT = 10
AD_PENALTY_WEIGHT = 20
KEYWORD_HIT_CAP = 5
SUPPORTING_REVIEW_CAP = 3
PRODUCT_LABEL_KEYWORDS = {
    "Hydrating": ["hydrating", "hydrate", "hydration", "moisture", "moisturizing"],
    "Acne": ["acne", "breakout", "breakouts", "blemish", "blemishes"],
    "Oil Control": ["oil control", "oil", "oily", "shine", "balance", "greasy"],
    "Brightening": ["brightening", "dark spots", "even tone", "fade marks"],
    "Soothing": ["soothing", "calming", "gentle", "redness"],
    "Smoothing": ["smooth", "smoother", "texture", "refine", "soft"],
}
CATEGORY_LABELS = {
    "cleanser": "Cleanser",
    "treatment": "Treatment",
    "moisturizer": "Moisturizer",
    "sunscreen": "Sunscreen",
    "skincare": "Product",
}


@dataclass
class ProductAggregate:
    asin: str
    label: str
    category: str
    skin_type: str
    average_rating: float
    representative_review: ProductReview
    supporting_reviews: list[ProductReview]
    review_count: int
    matched_skin_type: bool
    concern_hits: dict[str, list[str]]
    total_keyword_hits: int
    average_ad_score: float
    score_breakdown: dict[str, float]
    score: float


def build_amazon_url(asin: str) -> str:
    return f"https://www.amazon.com/dp/{asin}"


def count_concern_keyword_frequency(
    user_profile: UserProfileRequest,
    review: ProductReview,
) -> int:
    normalized_review = review.review.strip().lower()
    total_hits = 0

    for concern in get_normalized_concerns(user_profile):
        for keyword in CONCERN_KEYWORDS.get(concern, []):
            total_hits += normalized_review.count(keyword)

    return total_hits


def aggregate_concern_hits(
    user_profile: UserProfileRequest,
    reviews: list[ProductReview],
) -> tuple[dict[str, list[str]], int]:
    aggregated_hits: dict[str, list[str]] = {}
    total_keyword_hits = 0

    for review in reviews:
        total_keyword_hits += count_concern_keyword_frequency(user_profile, review)
        review_hits = get_concern_keyword_hits(user_profile, review)

        for concern, keywords in review_hits.items():
            existing_keywords = aggregated_hits.setdefault(concern, [])
            for keyword in keywords:
                if keyword not in existing_keywords:
                    existing_keywords.append(keyword)

    return aggregated_hits, total_keyword_hits


def infer_category(reviews: list[ProductReview]) -> str:
    categories = [review.category.strip().lower() for review in reviews if review.category.strip()]
    if not categories:
        return "skincare"

    return Counter(categories).most_common(1)[0][0]


def infer_category_label(reviews: list[ProductReview], category: str) -> str:
    if category != "skincare":
        return CATEGORY_LABELS.get(category, category.title() or "Product")

    normalized_reviews = " ".join(review.review.strip().lower() for review in reviews)
    if any(keyword in normalized_reviews for keyword in ["cleanser", "wash", "foam"]):
        return "Cleanser"
    if any(keyword in normalized_reviews for keyword in ["serum", "treatment", "gel", "spot"]):
        return "Treatment"
    if any(keyword in normalized_reviews for keyword in ["cream", "lotion", "moisturizer", "moisture"]):
        return "Moisturizer"
    if any(keyword in normalized_reviews for keyword in ["spf", "sunscreen", "sun screen"]):
        return "Sunscreen"

    return "Product"


def generate_product_label(reviews: list[ProductReview], category: str) -> str:
    normalized_reviews = " ".join(review.review.strip().lower() for review in reviews)
    label_counts = {
        label: sum(normalized_reviews.count(keyword) for keyword in keywords)
        for label, keywords in PRODUCT_LABEL_KEYWORDS.items()
    }
    top_label, top_count = max(label_counts.items(), key=lambda item: item[1], default=("", 0))
    category_label = infer_category_label(reviews, category)

    if top_count > 0:
        return f"{top_label} {category_label}"

    return category_label


def select_skin_type(
    reviews: list[ProductReview],
    normalized_skin_type: str,
) -> tuple[str, bool]:
    normalized_review_skin_types = [review.skin_type.strip().lower() for review in reviews]

    if normalized_skin_type in normalized_review_skin_types:
        matching_review = next(
            review for review in reviews if review.skin_type.strip().lower() == normalized_skin_type
        )
        return matching_review.skin_type, True

    dominant_skin_type = Counter(normalized_review_skin_types).most_common(1)[0][0]
    matching_review = next(
        review for review in reviews if review.skin_type.strip().lower() == dominant_skin_type
    )
    return matching_review.skin_type, False


def select_representative_review(
    user_profile: UserProfileRequest,
    reviews: list[ProductReview],
) -> ProductReview:
    return max(
        reviews,
        key=lambda review: (
            review.skin_type.strip().lower() == user_profile.skin_type.strip().lower(),
            len(get_concern_keyword_hits(user_profile, review)),
            count_concern_keyword_frequency(user_profile, review),
            review.rating,
        ),
    )


def build_score_breakdown(
    user_profile: UserProfileRequest,
    reviews: list[ProductReview],
    normalized_skin_type: str,
) -> tuple[dict[str, float], bool, dict[str, list[str]], int, float]:
    concern_hits, total_keyword_hits = aggregate_concern_hits(user_profile, reviews)
    supporting_reviews_count = len(reviews)
    average_rating = mean(review.rating for review in reviews)
    average_ad_score = mean(calculate_ad_score(review) for review in reviews)
    matched_skin_type = any(
        review.skin_type.strip().lower() == normalized_skin_type for review in reviews
    )
    normalized_concerns = get_normalized_concerns(user_profile)

    skin_type_score = float(SKIN_TYPE_WEIGHT if matched_skin_type else 0.0)
    concern_coverage_score = 0.0
    keyword_frequency_score = 0.0

    if normalized_concerns:
        concern_coverage_score = (
            len(concern_hits) / len(normalized_concerns)
        ) * CONCERN_COVERAGE_WEIGHT
        keyword_frequency_score = (
            min(total_keyword_hits, KEYWORD_HIT_CAP) / KEYWORD_HIT_CAP
        ) * KEYWORD_FREQUENCY_WEIGHT

    rating_score = (average_rating / 5) * RATING_WEIGHT
    supporting_reviews_score = (
        min(supporting_reviews_count, SUPPORTING_REVIEW_CAP) / SUPPORTING_REVIEW_CAP
    ) * SUPPORTING_REVIEWS_WEIGHT

    active_positive_max = SKIN_TYPE_WEIGHT + RATING_WEIGHT + SUPPORTING_REVIEWS_WEIGHT
    if normalized_concerns:
        active_positive_max += CONCERN_COVERAGE_WEIGHT + KEYWORD_FREQUENCY_WEIGHT

    score_breakdown = {
        "skin_type": round((skin_type_score / active_positive_max) * 100, 2),
        "concern_coverage": round((concern_coverage_score / active_positive_max) * 100, 2),
        "keyword_frequency": round((keyword_frequency_score / active_positive_max) * 100, 2),
        "rating": round((rating_score / active_positive_max) * 100, 2),
        "supporting_reviews": round(
            (supporting_reviews_score / active_positive_max) * 100,
            2,
        ),
        "ad_penalty": round(average_ad_score * AD_PENALTY_WEIGHT, 2),
    }

    return (
        score_breakdown,
        matched_skin_type,
        concern_hits,
        total_keyword_hits,
        round(average_ad_score, 2),
    )


def build_product_aggregate(
    user_profile: UserProfileRequest,
    product_reviews: list[ProductReview],
    normalized_skin_type: str,
) -> ProductAggregate:
    grouped_category = infer_category(product_reviews)
    representative_review = select_representative_review(user_profile, product_reviews)
    selected_skin_type, matched_skin_type = select_skin_type(product_reviews, normalized_skin_type)
    average_rating = round(mean(review.rating for review in product_reviews), 2)
    (
        score_breakdown,
        _,
        concern_hits,
        total_keyword_hits,
        average_ad_score,
    ) = build_score_breakdown(user_profile, product_reviews, normalized_skin_type)

    score = round(
        max(
            0.0,
            min(
                100.0,
                sum(
                    value
                    for key, value in score_breakdown.items()
                    if key != "ad_penalty"
                )
                - score_breakdown["ad_penalty"],
            ),
        ),
        2,
    )

    return ProductAggregate(
        asin=representative_review.product,
        label=generate_product_label(product_reviews, grouped_category),
        category=grouped_category,
        skin_type=selected_skin_type,
        average_rating=average_rating,
        representative_review=representative_review,
        supporting_reviews=product_reviews,
        review_count=len(product_reviews),
        matched_skin_type=matched_skin_type,
        concern_hits=concern_hits,
        total_keyword_hits=total_keyword_hits,
        average_ad_score=average_ad_score,
        score_breakdown=score_breakdown,
        score=score,
    )


def rank_products(
    user_profile: UserProfileRequest,
    reviews: list[ProductReview],
    limit: int = 3,
) -> tuple[list[Recommendation], str]:
    normalized_skin_type = user_profile.skin_type.strip().lower()
    grouped_reviews: dict[str, list[ProductReview]] = defaultdict(list)

    for review in reviews:
        grouped_reviews[review.product].append(review)

    product_aggregates = [
        build_product_aggregate(user_profile, product_reviews, normalized_skin_type)
        for product_reviews in grouped_reviews.values()
    ]
    exact_matches = [
        aggregate for aggregate in product_aggregates if aggregate.matched_skin_type
    ]
    non_matches = [
        aggregate for aggregate in product_aggregates if not aggregate.matched_skin_type
    ]

    exact_matches.sort(key=lambda aggregate: aggregate.score, reverse=True)
    non_matches.sort(key=lambda aggregate: aggregate.score, reverse=True)

    if exact_matches:
        ranked_products = (exact_matches + non_matches)[:limit]
        strategy = "exact_match_prioritized"
    else:
        ranked_products = sorted(
            product_aggregates,
            key=lambda aggregate: aggregate.score,
            reverse=True,
        )[:limit]
        strategy = "highest_rated_fallback"

    recommendations = [
        Recommendation(
            asin=aggregate.asin,
            label=aggregate.label,
            category=aggregate.category,
            skin_type=aggregate.skin_type,
            rating=aggregate.average_rating,
            review_count=aggregate.review_count,
            keyword_frequency=aggregate.total_keyword_hits,
            amazon_url=build_amazon_url(aggregate.asin),
            score=aggregate.score,
            review=aggregate.representative_review.review,
            ad_score=aggregate.average_ad_score,
            matched_skin_type=aggregate.matched_skin_type,
            reason=build_recommendation_reason(
                user_profile,
                aggregate.representative_review,
                len(aggregate.supporting_reviews),
                aggregate.average_rating,
                aggregate.concern_hits,
                aggregate.total_keyword_hits,
                aggregate.average_ad_score,
                aggregate.score_breakdown,
            ),
        )
        for aggregate in ranked_products
    ]

    return recommendations, strategy
