const form = document.getElementById("profile-form");
const status = document.getElementById("result-status");
const recommendationsList = document.getElementById("recommendations-list");
const apiBaseUrl = window.APP_CONFIG?.API_BASE_URL?.replace(/\/$/, "") || "";

function getApiUrl(path) {
  return apiBaseUrl ? `${apiBaseUrl}${path}` : path;
}

function renderRecommendations(recommendations) {
  recommendationsList.innerHTML = "";

  recommendations.forEach((recommendation, index) => {
    const card = document.createElement("article");
    card.className = "recommendation-card";

    card.innerHTML = `
      <h3>${index + 1}. ${recommendation.product}</h3>
      <p class="recommendation-meta">
        Skin type: ${recommendation.skin_type} | Rating: ${recommendation.rating.toFixed(1)}
      </p>
      <p class="recommendation-review">${recommendation.review}</p>
      <p class="recommendation-reason">${recommendation.reason}</p>
    `;

    recommendationsList.appendChild(card);
  });
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const concernsField = form.elements.namedItem("concerns");
  const payload = {
    skin_type: form.elements.namedItem("skin_type").value,
    concerns: Array.from(concernsField.selectedOptions, (option) => option.value),
    budget: Number(form.elements.namedItem("budget").value),
    preferences: form.elements.namedItem("preferences").value.trim() || null,
  };

  status.textContent = "Loading recommendations...";
  recommendationsList.innerHTML = "";

  try {
    const response = await fetch(getApiUrl("/api/profile"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Unable to load recommendations.");
    }

    const data = await response.json();

    if (!Array.isArray(data.recommendations) || data.recommendations.length === 0) {
      status.textContent = "No recommendations found.";
      return;
    }

    status.textContent =
      data.match_strategy === "highest_rated_fallback"
        ? "No exact skin type match found, so these are the highest rated options."
        : "Here are your top 3 personalized recommendations.";

    renderRecommendations(data.recommendations.slice(0, 3));
  } catch (error) {
    status.textContent = `Request failed: ${error.message}`;
    recommendationsList.innerHTML = "";
  }
});
