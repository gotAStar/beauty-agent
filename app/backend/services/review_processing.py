from app.backend.models.schemas import ReviewSubmissionRequest


SUBMISSION_KEYWORDS = {
    "acne": ["acne", "breakout", "breakouts", "blemish", "blemishes"],
    "dryness": ["dry", "dryness", "flaky", "parched"],
    "oily": ["oil", "oily", "greasy", "shine"],
    "hydration": ["hydrate", "hydrating", "hydration", "moisture", "moisturizing"],
}
SUBMISSION_PROMOTIONAL_PHRASES = [
    "buy now",
    "best ever",
    "discount",
]


def extract_review_keywords(review_text: str) -> list[str]:
    normalized_text = review_text.strip().lower()
    keywords: list[str] = []

    for keyword, phrases in SUBMISSION_KEYWORDS.items():
        if any(phrase in normalized_text for phrase in phrases):
            keywords.append(keyword)

    return keywords


def detect_promotional_content(review_text: str) -> bool:
    normalized_text = review_text.strip().lower()

    return any(phrase in normalized_text for phrase in SUBMISSION_PROMOTIONAL_PHRASES)


def process_review_submission(payload: ReviewSubmissionRequest) -> tuple[list[str], bool]:
    keywords = extract_review_keywords(payload.review_text)
    is_ad = detect_promotional_content(payload.review_text)

    return keywords, is_ad
