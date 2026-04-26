import asyncio
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.backend.api.routes import create_user_profile
from app.backend.models.schemas import ProductReview, UserProfileRequest
from app.backend.services.filtering import calculate_ad_score, filter_reviews
from app.backend.services.ingestion import load_reviews
from app.backend.services.ranking import rank_products
from app.backend.services.trust import calculate_trust_score


def test_load_reviews_reads_json_dataset() -> None:
    reviews = load_reviews()

    assert len(reviews) == 4
    assert reviews[0].product == "Oil Control Cleanser"


def test_filter_reviews_removes_promotional_reviews() -> None:
    reviews = [
        ProductReview(
            product="Trusted Cleanser",
            skin_type="oily",
            review="Helps reduce oil and acne",
            rating=4.5,
        ),
        ProductReview(
            product="Promo Serum",
            skin_type="oily",
            review="Amazing must buy product, best ever",
            rating=4.9,
        ),
        ProductReview(
            product="Influencer Cream",
            skin_type="dry",
            review="Link in bio for this amazing cream",
            rating=4.8,
        ),
    ]

    filtered_reviews, filtered_count = filter_reviews(reviews)

    assert filtered_count == 2
    assert [review.product for review in filtered_reviews] == ["Trusted Cleanser"]


def test_calculate_ad_score_scales_with_promotional_language() -> None:
    low_signal_review = ProductReview(
        product="Gentle Wash",
        skin_type="sensitive",
        review="Gentle and calming cleanser",
        rating=4.2,
    )
    high_signal_review = ProductReview(
        product="Promo Wash",
        skin_type="sensitive",
        review="Amazing must buy cleanser, best ever",
        rating=4.9,
    )

    assert calculate_ad_score(low_signal_review) == 0.0
    assert calculate_ad_score(high_signal_review) == 1.0


def test_calculate_trust_score_rewards_clean_consistent_review_sets() -> None:
    trusted_reviews = [
        ProductReview(
            product="Cleanser A",
            skin_type="oily",
            review="Helps reduce oil",
            rating=4.5,
        ),
        ProductReview(
            product="Cleanser B",
            skin_type="oily",
            review="Controls shine well",
            rating=4.6,
        ),
        ProductReview(
            product="Cleanser C",
            skin_type="oily",
            review="Good daily cleanser",
            rating=4.4,
        ),
        ProductReview(
            product="Cleanser D",
            skin_type="oily",
            review="Works consistently",
            rating=4.5,
        ),
    ]
    lower_trust_reviews = [
        ProductReview(
            product="Mixed A",
            skin_type="oily",
            review="Fine result",
            rating=5.0,
        ),
        ProductReview(
            product="Mixed B",
            skin_type="oily",
            review="Not great",
            rating=2.0,
        ),
    ]

    high_score = calculate_trust_score(
        trusted_reviews,
        filtered_reviews_count=0,
        total_reviews_analyzed=4,
    )
    low_score = calculate_trust_score(
        lower_trust_reviews,
        filtered_reviews_count=2,
        total_reviews_analyzed=4,
    )

    assert 0 <= high_score <= 100
    assert 0 <= low_score <= 100
    assert high_score > low_score


def test_calculate_trust_score_returns_zero_without_reviews() -> None:
    assert calculate_trust_score([], filtered_reviews_count=0, total_reviews_analyzed=0) == 0


def test_rank_products_prioritizes_skin_type_match_then_rating() -> None:
    reviews = [
        ProductReview(
            product="Match High",
            skin_type="oily",
            review="Best oily option",
            rating=4.8,
        ),
        ProductReview(
            product="Match Mid",
            skin_type="oily",
            review="Solid oily option",
            rating=4.3,
        ),
        ProductReview(
            product="Fallback Top",
            skin_type="dry",
            review="Best fallback",
            rating=5.0,
        ),
        ProductReview(
            product="Fallback Next",
            skin_type="combination",
            review="Next fallback",
            rating=4.7,
        ),
    ]

    recommendations, strategy = rank_products(
        UserProfileRequest(skin_type="oily"),
        reviews,
    )

    assert strategy == "exact_match_prioritized"
    assert [recommendation.product for recommendation in recommendations] == [
        "Match High",
        "Match Mid",
        "Fallback Top",
    ]
    assert recommendations[0].matched_skin_type is True
    assert recommendations[2].matched_skin_type is False
    assert recommendations[0].ad_score == 0.0


def test_rank_products_boosts_concern_matches_in_review_text() -> None:
    reviews = [
        ProductReview(
            product="Higher Rated Basic Gel",
            skin_type="oily",
            review="Light texture for everyday use",
            rating=4.6,
        ),
        ProductReview(
            product="Acne Support Serum",
            skin_type="oily",
            review="Helps reduce acne and breakouts fast",
            rating=4.4,
        ),
        ProductReview(
            product="Fallback Cream",
            skin_type="dry",
            review="Very moisturizing",
            rating=4.8,
        ),
    ]

    recommendations, strategy = rank_products(
        UserProfileRequest(skin_type="oily", concerns=["acne"]),
        reviews,
    )

    assert strategy == "exact_match_prioritized"
    assert recommendations[0].product == "Acne Support Serum"
    assert "Helps reduce acne and breakouts fast" in recommendations[0].reason
    assert "Positive signals:" in recommendations[0].reason
    assert "Negative signals:" in recommendations[0].reason
    assert "acne support" in recommendations[0].reason


def test_rank_products_falls_back_to_highest_rated_when_no_match() -> None:
    reviews = [
        ProductReview(
            product="Dry Pick",
            skin_type="dry",
            review="Top dry option",
            rating=4.9,
        ),
        ProductReview(
            product="Combo Pick",
            skin_type="combination",
            review="Great combo option",
            rating=4.6,
        ),
        ProductReview(
            product="Sensitive Pick",
            skin_type="sensitive",
            review="Gentle option",
            rating=4.4,
        ),
    ]

    recommendations, strategy = rank_products(
        UserProfileRequest(skin_type="oily"),
        reviews,
    )

    assert strategy == "highest_rated_fallback"
    assert [recommendation.product for recommendation in recommendations] == [
        "Dry Pick",
        "Combo Pick",
        "Sensitive Pick",
    ]


def test_profile_route_returns_top_three_recommendations() -> None:
    response = asyncio.run(create_user_profile(UserProfileRequest(skin_type="combination")))

    assert response.user_profile.skin_type == "combination"
    assert response.match_strategy == "exact_match_prioritized"
    assert response.filtered_reviews_count == 0
    assert response.total_reviews_analyzed == 4
    assert 0 <= response.trust_score <= 100
    assert len(response.recommendations) == 3
    assert response.recommendations[0].product == "Lightweight Moisturizer"


def test_profile_route_uses_concern_keywords_for_dataset() -> None:
    response = asyncio.run(
        create_user_profile(
            UserProfileRequest(
                skin_type="dry",
                concerns=["dryness"],
            )
        )
    )

    assert response.recommendations[0].product == "Hydrating Cream"
    assert "Very moisturizing and gentle" in response.recommendations[0].reason
    assert "dryness support" in response.recommendations[0].reason


def test_recommendation_reason_includes_negative_signals_for_fallbacks() -> None:
    reviews = [
        ProductReview(
            product="Dry Rescue Cream",
            skin_type="dry",
            review="Very moisturizing and calming",
            rating=4.6,
        ),
        ProductReview(
            product="Oily Gel",
            skin_type="oily",
            review="Light everyday gel",
            rating=4.8,
        ),
    ]

    recommendations, _ = rank_products(
        UserProfileRequest(skin_type="oily", concerns=["dryness"]),
        reviews,
    )

    assert recommendations[1].product == "Dry Rescue Cream"
    assert "product is labeled for dry skin, not oily" in recommendations[1].reason
    assert "Review says: \"Very moisturizing and calming\"" in recommendations[1].reason


def test_recommendation_reason_avoids_empty_positive_signals_for_weak_matches() -> None:
    reviews = [
        ProductReview(
            product="Neutral Lotion",
            skin_type="combination",
            review="Good balance and light feel",
            rating=4.3,
        ),
    ]

    recommendations, _ = rank_products(
        UserProfileRequest(skin_type="oily", concerns=["acne"]),
        reviews,
    )

    assert "Positive signals: ." not in recommendations[0].reason
    assert "limited direct evidence beyond passing the review quality filter" in recommendations[0].reason


def test_profile_route_excludes_high_ad_score_reviews_from_results() -> None:
    promotional_review = ProductReview(
        product="Promo Gel",
        skin_type="combination",
        review="Amazing must buy gel, link in bio",
        rating=5.0,
    )
    trusted_review = ProductReview(
        product="Balanced Lotion",
        skin_type="combination",
        review="Good balance and light feel",
        rating=4.3,
    )

    filtered_reviews, filtered_count = filter_reviews([promotional_review, trusted_review])
    recommendations, strategy = rank_products(
        UserProfileRequest(skin_type="combination"),
        filtered_reviews,
    )

    assert filtered_count == 1
    assert strategy == "exact_match_prioritized"
    assert [recommendation.product for recommendation in recommendations] == ["Balanced Lotion"]
