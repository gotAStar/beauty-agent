from pydantic import AliasChoices, BaseModel, Field


class UserProfileRequest(BaseModel):
    category: str = Field(default="all")
    skin_type: str = Field(default="combination")
    concerns: list[str] = Field(default_factory=list)
    budget: float = Field(default=50)
    preferences: str | None = None


class ProductReview(BaseModel):
    product: str = Field(validation_alias=AliasChoices("product_name", "product"))
    category: str = Field(default="skincare")
    skin_type: str
    review: str
    rating: float


class Recommendation(BaseModel):
    asin: str
    label: str
    category: str
    skin_type: str
    rating: float
    review_count: int
    keyword_frequency: int
    amazon_url: str
    score: float
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


class ReviewSubmissionRequest(BaseModel):
    category: str = Field(default="skincare", min_length=1)
    review_text: str = Field(min_length=1)
    skin_type: str = Field(min_length=1)
    rating: float = Field(ge=0, le=5)


class ReviewSubmissionResponse(BaseModel):
    success: bool
    message: str
    keywords: list[str]
    is_ad: bool
