export function formatCategory(value) {
  if (!value) {
    return "";
  }

  return value.charAt(0).toUpperCase() + value.slice(1);
}

function extractSection(text, label) {
  const pattern = new RegExp(
    `${label}:\\s*(.*?)(?=(Positive signals:|Negative signals:|Review says:|Score breakdown:|$))`,
    "is",
  );
  const match = text.match(pattern);

  if (!match) {
    return "";
  }

  return match[1].replace(/\s+/g, " ").trim().replace(/\.$/, "");
}

function extractReviewQuote(text, fallbackReview) {
  const match = text.match(/Review says:\s*"([^"]+)"/i);
  const sourceText = match?.[1] || fallbackReview || "";
  return sourceText.replace(/\s+/g, " ").trim();
}

export function extractRecommendationInsights(recommendation) {
  return {
    positive: extractSection(recommendation.reason, "Positive signals"),
    negative: extractSection(recommendation.reason, "Negative signals"),
    reviewQuote: extractReviewQuote(recommendation.reason, recommendation.review),
  };
}

export function buildSignalItems(recommendation) {
  const { positive, negative, reviewQuote } = extractRecommendationInsights(recommendation);
  const signals = [];

  if (positive) {
    signals.push({
      icon: "\u2714",
      tone: "positive",
      text: positive,
    });
  }

  if (reviewQuote) {
    signals.push({
      icon: "\u2b50",
      tone: "neutral",
      text: `Review highlight: "${reviewQuote}"`,
    });
  }

  if (negative) {
    signals.push({
      icon: "\u274c",
      tone: "negative",
      text: negative,
    });
  }

  if (signals.length < 3) {
    signals.push({
      icon: "\u2b50",
      tone: "neutral",
      text: `Rated ${recommendation.rating.toFixed(1)}/5 across ${recommendation.review_count} review(s) with a recommendation score of ${recommendation.score.toFixed(1)}.`,
    });
  }

  if (signals.length < 3) {
    signals.push({
      icon: recommendation.matched_skin_type ? "\u2714" : "\u274c",
      tone: recommendation.matched_skin_type ? "positive" : "negative",
      text: recommendation.matched_skin_type
        ? `Labeled for ${recommendation.skin_type} skin, which matches your profile.`
        : `This product is labeled for ${recommendation.skin_type} skin, so it is more of a fallback match.`,
    });
  }

  return signals.slice(0, 3);
}
