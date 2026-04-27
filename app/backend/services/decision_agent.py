from app.backend.models.schemas import (
    AgentStep,
    FinalDecision,
    Recommendation,
    UserProfileRequest,
    UserProfileResponse,
)
from app.backend.services.filtering import filter_reviews
from app.backend.services.ingestion import load_reviews
from app.backend.services.ranking import rank_products
from app.backend.services.trust import calculate_trust_score


def _format_profile_goal(user_profile: UserProfileRequest) -> str:
    concerns = ", ".join(user_profile.concerns) if user_profile.concerns else "general skin support"
    preferences = user_profile.preferences or "no extra preferences provided"
    return (
        f"Choose the best {user_profile.category} option for {user_profile.skin_type} skin, "
        f"prioritizing {concerns}, within a budget of {user_profile.budget:.0f}, "
        f"with {preferences}."
    )


def _build_decision_tradeoffs(
    chosen_product: Recommendation,
    alternatives: list[Recommendation],
) -> list[str]:
    trade_offs: list[str] = []

    if not chosen_product.matched_skin_type:
        trade_offs.append(
            f"{chosen_product.label} is a fallback pick because no exact {chosen_product.skin_type} skin match beat it."
        )

    if chosen_product.review_count <= 1:
        trade_offs.append("The choice is supported by only one valid review, so the evidence base is still thin.")

    if chosen_product.ad_score > 0:
        trade_offs.append(
            f"Some supporting reviews have light promotional language risk (ad score {chosen_product.ad_score:.2f})."
        )

    if alternatives:
        strongest_alternative = alternatives[0]
        if strongest_alternative.rating > chosen_product.rating:
            trade_offs.append(
                f"{strongest_alternative.label} has a slightly higher rating, but the chosen product fit your profile better overall."
            )
        elif strongest_alternative.review_count > chosen_product.review_count:
            trade_offs.append(
                f"{strongest_alternative.label} has broader review support, but its total personalization score was lower."
            )

    if not trade_offs:
        trade_offs.append("This option showed the strongest balance of personalization, review quality, and trust signals.")

    return trade_offs


def _build_confidence_score(
    chosen_product: Recommendation,
    trust_score: int,
) -> int:
    confidence_score = (
        (trust_score * 0.45)
        + (chosen_product.score * 0.4)
        + (min(chosen_product.review_count, 5) * 3)
        + (6 if chosen_product.matched_skin_type else 0)
    )
    return max(0, min(100, round(confidence_score)))


def _build_final_decision(
    recommendations: list[Recommendation],
    trust_score: int,
) -> FinalDecision:
    if not recommendations:
        return FinalDecision(
            reasoning="No product had enough filtered evidence to support a confident decision for this profile yet.",
            trade_offs=[
                "The agent could not produce a reliable winner from the currently available review set."
            ],
            confidence_score=0,
        )

    chosen_product = recommendations[0]
    alternatives = recommendations[1:]
    reasoning = (
        f"{chosen_product.label} is the agent's top choice because it achieved the highest overall decision score "
        f"({chosen_product.score:.1f}) after review filtering and product ranking. {chosen_product.reason}"
    )

    return FinalDecision(
        chosen_product=chosen_product,
        reasoning=reasoning,
        trade_offs=_build_decision_tradeoffs(chosen_product, alternatives),
        confidence_score=_build_confidence_score(chosen_product, trust_score),
    )


def decision_agent(
    user_profile: UserProfileRequest,
    db,
) -> UserProfileResponse:
    agent_steps: list[AgentStep] = []

    agent_steps.append(
        AgentStep(
            key="goal_understanding",
            title="Goal Understanding",
            summary="Understood the user's category, skin profile, and decision priorities.",
            details=[_format_profile_goal(user_profile)],
            metrics={
                "selected_concerns": len(user_profile.concerns),
                "budget": user_profile.budget,
            },
        )
    )

    reviews = load_reviews(db)
    category_reviews = reviews
    category_match_found = False
    if user_profile.category != "all":
        matching_category_reviews = [
            review
            for review in reviews
            if review.category.strip().lower() == user_profile.category.strip().lower()
        ]
        if matching_category_reviews:
            category_reviews = matching_category_reviews
            category_match_found = True

    agent_steps.append(
        AgentStep(
            key="data_retrieval",
            title="Data Retrieval",
            summary="Loaded review evidence and narrowed it to the requested category when possible.",
            details=[
                f"Loaded {len(reviews)} total reviews from the available data sources.",
                (
                    f"Matched {len(category_reviews)} reviews in the {user_profile.category} category."
                    if category_match_found or user_profile.category == "all"
                    else f"No exact category rows were found for {user_profile.category}, so the agent kept the broader review pool."
                ),
            ],
            metrics={
                "total_reviews_loaded": len(reviews),
                "category_reviews": len(category_reviews),
            },
        )
    )

    filtered_reviews, filtered_reviews_count = filter_reviews(category_reviews)
    agent_steps.append(
        AgentStep(
            key="filtering",
            title="Filtering",
            summary="Removed suspicious or highly promotional review evidence before scoring products.",
            details=[
                f"Started with {len(category_reviews)} review(s) in the working set.",
                f"Filtered out {filtered_reviews_count} review(s) with high ad or promotional signals.",
                f"Kept {len(filtered_reviews)} valid review(s) for ranking.",
            ],
            metrics={
                "input_reviews": len(category_reviews),
                "filtered_reviews": filtered_reviews_count,
                "valid_reviews": len(filtered_reviews),
            },
        )
    )

    recommendations, strategy = rank_products(user_profile, filtered_reviews)
    unique_products = len({review.product for review in filtered_reviews})
    agent_steps.append(
        AgentStep(
            key="ranking",
            title="Ranking",
            summary="Grouped valid reviews into products, scored them, and created a shortlist.",
            details=[
                f"Evaluated {unique_products} product candidate(s) after grouping reviews by product.",
                f"Used the {strategy} strategy to prioritize the shortlist.",
                f"Produced {len(recommendations)} recommendation candidate(s).",
            ],
            metrics={
                "products_ranked": unique_products,
                "shortlist_size": len(recommendations),
                "match_strategy": strategy,
            },
        )
    )

    trust_score = calculate_trust_score(
        filtered_reviews,
        filtered_reviews_count,
        len(category_reviews),
    )
    final_decision = _build_final_decision(recommendations, trust_score)

    if final_decision.chosen_product is not None:
        decision_details = [
            f"Selected {final_decision.chosen_product.label} as the strongest product-level decision.",
            f"Confidence score: {final_decision.confidence_score}/100.",
        ]
    else:
        decision_details = [
            "No product cleared the threshold for a confident final decision.",
            "The agent returned the filtering and ranking context so the gap is explainable.",
        ]

    agent_steps.append(
        AgentStep(
            key="decision",
            title="Decision",
            summary="Turned the ranked shortlist into one final recommendation with explicit trade-offs.",
            details=decision_details + final_decision.trade_offs,
            metrics={
                "trust_score": trust_score,
                "confidence_score": final_decision.confidence_score,
            },
        )
    )

    return UserProfileResponse(
        user_profile=user_profile,
        final_decision=final_decision,
        agent_steps=agent_steps,
        recommendations=recommendations,
        match_strategy=strategy,
        filtered_reviews_count=filtered_reviews_count,
        total_reviews_analyzed=len(category_reviews),
        trust_score=trust_score,
    )
