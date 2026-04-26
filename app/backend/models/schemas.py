from pydantic import BaseModel, Field


class UserProfileRequest(BaseModel):
    skin_type: str = Field(default="combination")
    concerns: list[str] = Field(default_factory=list)
    budget: float = Field(default=50)
    preferences: str | None = None


class ProductReview(BaseModel):
    product: str
    skin_type: str
    review: str
    rating: float


class Recommendation(BaseModel):
    product: str
    skin_type: str
    rating: float
    review: str
    ad_score: float
    matched_skin_type: bool
    reason: str


class UserProfileResponse(BaseModel):
    user_profile: UserProfileRequest
    recommendations: list[Recommendation]
    match_strategy: str
    filtered_reviews_count: int
    total_reviews_analyzed: int
    trust_score: int
