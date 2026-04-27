import logging
import json
from app.backend.database import get_database_url
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.backend.db_models import ReviewRecord
from app.backend.models.schemas import ProductReview


BASE_DIR = Path(__file__).resolve().parents[3]
REVIEWS_PATH = BASE_DIR / "data" / "reviews.json"
logger = logging.getLogger(__name__)


def load_seed_reviews() -> list[ProductReview]:
    with REVIEWS_PATH.open(encoding="utf-8") as reviews_file:
        raw_reviews = json.load(reviews_file)

    return [ProductReview.model_validate(review) for review in raw_reviews]


def load_database_reviews(db: Session) -> list[ProductReview]:
    try:
        saved_reviews = db.query(ReviewRecord).all()
    except SQLAlchemyError as exc:
        logger.warning("Unable to load database reviews, falling back to seed data only: %s", exc)
        return []

    return [
        ProductReview(
            product=review.product_name,
            category=review.category or "skincare",
            skin_type=review.skin_type,
            review=review.review_text,
            rating=review.rating,
        )
        for review in saved_reviews
    ]


def load_reviews(db: Session) -> list[ProductReview]:
    database_reviews = load_database_reviews(db)

    if database_reviews:
        logger.info("Loaded %s reviews from database; skipping seed fallback data.", len(database_reviews))
        return database_reviews

    database_url = get_database_url()
    if not database_url.startswith("sqlite"):
        logger.warning(
            "No database reviews found for configured database %s; not falling back to seed data.",
            database_url,
        )
        return []

    seed_reviews = load_seed_reviews()
    logger.info("No database reviews found; using %s seed reviews.", len(seed_reviews))
    return seed_reviews
