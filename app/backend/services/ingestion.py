from functools import lru_cache
import json
from pathlib import Path

from app.backend.models.schemas import ProductReview


BASE_DIR = Path(__file__).resolve().parents[3]
REVIEWS_PATH = BASE_DIR / "data" / "reviews.json"


@lru_cache(maxsize=1)
def load_reviews() -> list[ProductReview]:
    with REVIEWS_PATH.open(encoding="utf-8") as reviews_file:
        raw_reviews = json.load(reviews_file)

    return [ProductReview.model_validate(review) for review in raw_reviews]
