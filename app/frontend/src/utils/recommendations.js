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

export function buildSignalItems(recommendation) {
  const positive = extractSection(recommendation.reason, "Positive signals");
  const negative = extractSection(recommendation.reason, "Negative signals");
  const reviewQuote = extractReviewQuote(recommendation.reason, recommendation.review);
  const signals = [];

  if (positive) {
    signals.push({
      icon: "✔",
      tone: "positive",
      text: positive,
    });
  }

  if (reviewQuote) {
    signals.push({
      icon: "⭐",
      tone: "neutral",
      text: `Review highlight: "${reviewQuote}"`,
    });
  }

  if (negative) {
    signals.push({
      icon: "❌",
      tone: "negative",
      text: negative,
    });
  }

  if (signals.length < 3) {
    signals.push({
      icon: "⭐",
      tone: "neutral",
      text: `Rated ${recommendation.rating.toFixed(1)}/5 with a recommendation score of ${recommendation.score.toFixed(1)}.`,
    });
  }

  if (signals.length < 3) {
    signals.push({
      icon: recommendation.matched_skin_type ? "✔" : "❌",
      tone: recommendation.matched_skin_type ? "positive" : "negative",
      text: recommendation.matched_skin_type
        ? `Labeled for ${recommendation.skin_type} skin, which matches your profile.`
        : `This product is labeled for ${recommendation.skin_type} skin, so it is more of a fallback match.`,
    });
  }

  return signals.slice(0, 3);
}
