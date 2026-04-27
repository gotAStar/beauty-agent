const categoryForm = document.getElementById("category-form");
const categoryStep = document.getElementById("category-step");
const profileStep = document.getElementById("profile-step");
const form = document.getElementById("profile-form");
const status = document.getElementById("result-status");
const recommendationsList = document.getElementById("recommendations-list");
const reviewForm = document.getElementById("review-form");
const reviewStatus = document.getElementById("review-status");
const selectedCategoryLabel = document.getElementById("selected-category");
const backToCategoryButton = document.getElementById("back-to-category");
const apiBaseUrl = window.APP_CONFIG?.API_BASE_URL?.replace(/\/$/, "") || "";

function getApiUrl(path) {
  return apiBaseUrl ? `${apiBaseUrl}${path}` : path;
}

function formatCategory(category) {
  return category.charAt(0).toUpperCase() + category.slice(1);
}

function showProfileStep(category) {
  form.elements.namedItem("category").value = category;
  selectedCategoryLabel.textContent = `Selected category: ${formatCategory(category)}`;
  categoryStep.classList.add("hidden");
  profileStep.classList.remove("hidden");
}

function showCategoryStep() {
  profileStep.classList.add("hidden");
  categoryStep.classList.remove("hidden");
}

function renderRecommendations(recommendations) {
  recommendationsList.innerHTML = "";

  recommendations.forEach((recommendation, index) => {
    const card = document.createElement("article");
    card.className = "recommendation-card";

    card.innerHTML = `
      <h3>${index + 1}. ${recommendation.product}</h3>
      <p class="recommendation-meta">
        Skin type: ${recommendation.skin_type} | Rating: ${recommendation.rating.toFixed(1)} | Score: ${recommendation.score.toFixed(1)}
      </p>
      <p class="recommendation-review">${recommendation.review}</p>
      <p class="recommendation-reason">${recommendation.reason}</p>
    `;

    recommendationsList.appendChild(card);
  });
}

categoryForm.addEventListener("submit", (event) => {
  event.preventDefault();

  const selectedCategory = categoryForm.elements.namedItem("category").value;
  showProfileStep(selectedCategory);
});

backToCategoryButton.addEventListener("click", () => {
  showCategoryStep();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const concernsField = form.elements.namedItem("concerns");
  const payload = {
    category: form.elements.namedItem("category").value,
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

reviewForm.addEventListener("submit", async (event) => {
  event.preventDefault();

  const payload = {
    category: reviewForm.elements.namedItem("review_category").value,
    review_text: reviewForm.elements.namedItem("review_text").value.trim(),
    skin_type: reviewForm.elements.namedItem("review_skin_type").value,
    rating: Number(reviewForm.elements.namedItem("review_rating").value),
  };

  reviewStatus.textContent = "Submitting review...";

  try {
    const response = await fetch(getApiUrl("/api/review"), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Unable to submit review.");
    }

    const data = await response.json();
    reviewStatus.textContent = `${data.message} Keywords: ${data.keywords.join(", ") || "none"}. Ad flag: ${data.is_ad}.`;
    reviewForm.reset();
  } catch (error) {
    reviewStatus.textContent = `Review submission failed: ${error.message}`;
  }
});
