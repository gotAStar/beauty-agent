import asyncio
from pathlib import Path
import sys
import uuid

import pytest
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.backend.api.routes import create_review, create_user_profile
from app.backend.database import get_session_factory, init_database, reset_database_state
from app.backend.db_models import ReviewRecord
from app.backend.models.schemas import (
    ProductReview,
    ReviewSubmissionRequest,
    UserProfileRequest,
)
from app.backend.services.filtering import calculate_ad_score, filter_reviews
from app.backend.services.ingestion import load_reviews
from app.backend.services.ranking import rank_products
from app.backend.services.review_processing import (
    detect_promotional_content,
    extract_review_keywords,
)
from app.backend.services.trust import calculate_trust_score


@pytest.fixture
def test_db(monkeypatch: pytest.MonkeyPatch):
    database_path = Path(__file__).resolve().parents[1] / f"test_reviews_{uuid.uuid4().hex}.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")
    reset_database_state()
    init_database()
    session = get_session_factory()()

    try:
        yield session
    finally:
        session.close()
        reset_database_state()
        if database_path.exists():
            database_path.unlink()


def test_load_reviews_reads_seed_dataset(test_db) -> None:
    reviews = load_reviews(test_db)

    assert len(reviews) == 4
    assert reviews[0].product == "Oil Control Cleanser"


def test_load_reviews_falls_back_to_seed_data_when_database_query_fails(
    test_db,
) -> None:
    class BrokenQuery:
        def all(self):
            raise SQLAlchemyError("database unavailable")

    class BrokenSession:
        def query(self, _model):
            return BrokenQuery()

    reviews = load_reviews(BrokenSession())

    assert len(reviews) == 4
    assert [review.product for review in reviews] == [
        "Oil Control Cleanser",
        "Acne Treatment Gel",
        "Hydrating Cream",
        "Lightweight Moisturizer",
    ]


def test_extract_review_keywords_detects_supported_categories() -> None:
    keywords = extract_review_keywords(
        "Hydrating formula helped my acne and reduced oily shine.",
    )

    assert keywords == ["acne", "oily", "hydration"]


def test_detect_promotional_content_flags_promotions() -> None:
    assert detect_promotional_content("Buy now for the best ever glow with discount code") is True
    assert detect_promotional_content("Gentle cleanser for daily use") is False


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
        review="Amazing must buy cleanser, link in bio, best ever",
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
    assert [recommendation.asin for recommendation in recommendations] == [
        "Match High",
        "Match Mid",
        "Fallback Top",
    ]
    assert recommendations[0].label == "Oil Control Product"
    assert recommendations[0].review_count == 1
    assert recommendations[0].amazon_url == "https://www.amazon.com/dp/Match High"
    assert recommendations[0].matched_skin_type is True
    assert recommendations[2].matched_skin_type is False
    assert recommendations[0].ad_score == 0.0
    assert recommendations[0].score > recommendations[1].score


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
    assert recommendations[0].asin == "Acne Support Serum"
    assert recommendations[0].label == "Acne Product"
    assert "Helps reduce acne and breakouts fast" in recommendations[0].reason
    assert "Positive signals:" in recommendations[0].reason
    assert "Negative signals:" in recommendations[0].reason
    assert "acne support" in recommendations[0].reason
    assert recommendations[0].score > recommendations[1].score


def test_rank_products_boosts_products_with_more_supporting_reviews() -> None:
    reviews = [
        ProductReview(
            product="Acne Rescue",
            skin_type="oily",
            review="Helps reduce acne and breakouts",
            rating=4.4,
        ),
        ProductReview(
            product="Acne Rescue",
            skin_type="oily",
            review="Good for acne prone oily skin",
            rating=4.3,
        ),
        ProductReview(
            product="Single Review Gel",
            skin_type="oily",
            review="Helps reduce acne",
            rating=4.6,
        ),
    ]

    recommendations, _ = rank_products(
        UserProfileRequest(skin_type="oily", concerns=["acne"]),
        reviews,
    )

    assert recommendations[0].asin == "Acne Rescue"
    assert recommendations[0].review_count == 2
    assert recommendations[0].score > recommendations[1].score
    assert "supported by 2 valid reviews" in recommendations[0].reason


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
    assert [recommendation.asin for recommendation in recommendations] == [
        "Dry Pick",
        "Combo Pick",
        "Sensitive Pick",
    ]


def test_rank_products_penalizes_mild_promotional_language() -> None:
    reviews = [
        ProductReview(
            product="Balanced Gel",
            skin_type="combination",
            review="Good balance and lightweight feel",
            rating=4.5,
        ),
        ProductReview(
            product="Promo Balance Gel",
            skin_type="combination",
            review="Amazing balance and lightweight feel",
            rating=4.5,
        ),
    ]

    recommendations, _ = rank_products(
        UserProfileRequest(skin_type="combination"),
        reviews,
    )

    assert recommendations[0].asin == "Balanced Gel"
    assert recommendations[1].ad_score > recommendations[0].ad_score
    assert "ad penalty" in recommendations[1].reason


def test_profile_route_returns_top_three_recommendations(test_db) -> None:
    response = asyncio.run(
        create_user_profile(UserProfileRequest(skin_type="combination"), db=test_db),
    )

    assert response.user_profile.skin_type == "combination"
    assert response.match_strategy == "exact_match_prioritized"
    assert response.filtered_reviews_count == 0
    assert response.total_reviews_analyzed == 4
    assert 0 <= response.trust_score <= 100
    assert len(response.recommendations) == 3
    assert response.recommendations[0].asin == "Lightweight Moisturizer"
    assert response.recommendations[0].label == "Oil Control Moisturizer"
    assert response.recommendations[0].score >= response.recommendations[1].score


def test_profile_route_uses_concern_keywords_for_dataset(test_db) -> None:
    response = asyncio.run(
        create_user_profile(
            UserProfileRequest(
                category="moisturizer",
                skin_type="dry",
                concerns=["dryness"],
            ),
            db=test_db,
        )
    )

    assert response.recommendations[0].asin == "Hydrating Cream"
    assert response.recommendations[0].label == "Hydrating Moisturizer"
    assert "Very moisturizing and gentle" in response.recommendations[0].reason
    assert "dryness support" in response.recommendations[0].reason


def test_profile_route_filters_by_category_first(test_db) -> None:
    response = asyncio.run(
        create_user_profile(
            UserProfileRequest(
                category="cleanser",
                skin_type="oily",
                concerns=["oily"],
            ),
            db=test_db,
        )
    )

    assert response.total_reviews_analyzed == 1
    assert [recommendation.asin for recommendation in response.recommendations] == [
        "Oil Control Cleanser"
    ]


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

    assert recommendations[1].asin == "Dry Rescue Cream"
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
    assert "review does not clearly mention your selected concerns" in recommendations[0].reason
    assert "Score breakdown:" in recommendations[0].reason


def test_review_submission_saves_to_database(test_db) -> None:
    response = asyncio.run(
        create_review(
            ReviewSubmissionRequest(
                category="treatment",
                review_text="Hydrating formula that helped my acne and oily skin.",
                skin_type="oily",
                rating=4.8,
            ),
            db=test_db,
        )
    )

    saved_reviews = test_db.query(ReviewRecord).all()

    assert response.success is True
    assert response.keywords == ["acne", "oily", "hydration"]
    assert response.is_ad is False
    assert len(saved_reviews) == 1
    assert saved_reviews[0].product_name == "user_submitted"
    assert saved_reviews[0].category == "treatment"
    assert saved_reviews[0].keywords == ["acne", "oily", "hydration"]


def test_review_submission_allows_duplicate_review_text(test_db) -> None:
    payload = ReviewSubmissionRequest(
        category="moisturizer",
        review_text="Same text review",
        skin_type="dry",
        rating=4.1,
    )

    asyncio.run(create_review(payload, db=test_db))
    asyncio.run(create_review(payload, db=test_db))

    saved_count = test_db.query(ReviewRecord).filter_by(review_text="Same text review").count()

    assert saved_count == 2


def test_review_submission_flags_promotional_content(test_db) -> None:
    response = asyncio.run(
        create_review(
            ReviewSubmissionRequest(
                category="cleanser",
                review_text="Buy now, best ever cleanser with discount today",
                skin_type="combination",
                rating=4.7,
            ),
            db=test_db,
        )
    )

    assert response.is_ad is True


def test_submitted_reviews_are_included_in_recommendations(test_db) -> None:
    asyncio.run(
        create_review(
            ReviewSubmissionRequest(
                category="moisturizer",
                review_text="Hydrating support for dry skin with great moisture",
                skin_type="dry",
                rating=5.0,
            ),
            db=test_db,
        )
    )

    response = asyncio.run(
        create_user_profile(
            UserProfileRequest(category="moisturizer", skin_type="dry", concerns=["dryness"]),
            db=test_db,
        )
    )

    assert response.total_reviews_analyzed == 3
    assert any(recommendation.asin == "user_submitted" for recommendation in response.recommendations)


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
    assert [recommendation.asin for recommendation in recommendations] == ["Balanced Lotion"]
