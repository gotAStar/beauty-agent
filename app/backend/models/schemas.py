from pydantic import AliasChoices, BaseModel, Field


class UserProfileRequest(BaseModel):
    category: str = Field(default="all")
    skin_type: str = Field(default="combination")
    concerns: list[str] = Field(default_factory=list)
    budget: float = Field(default=50)
    preferences: str | None = None


class ProductReview(BaseModel):
    product: str = Field(validation_alias=AliasChoices("product_name", "product"))
    asin: str | None = Field(default=None, validation_alias=AliasChoices("ASIN", "asin"))
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
    promotion_score: float
    consistency_score: int
    hidden_gem_score: int
    product_classification: str
    marketing_bias_warning: str | None = None
    matched_skin_type: bool
    reason: str


class AgentStep(BaseModel):
    key: str
    title: str
    status: str = Field(default="completed")
    summary: str
    details: list[str] = Field(default_factory=list)
    metrics: dict[str, int | float | str] = Field(default_factory=dict)


class FinalDecision(BaseModel):
    chosen_product: Recommendation | None = None
    reasoning: str
    trade_offs: list[str] = Field(default_factory=list)
    confidence_score: int = Field(default=0, ge=0, le=100)


class UserProfileResponse(BaseModel):
    user_profile: UserProfileRequest
    final_decision: FinalDecision
    agent_steps: list[AgentStep]
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
