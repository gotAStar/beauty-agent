const defaultApiBaseUrl = "https://beauty-agent-cufm.onrender.com";
const apiBaseUrl = (
  import.meta.env.API_BASE_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  defaultApiBaseUrl
).replace(/\/$/, "");

function getApiUrl(path) {
  return apiBaseUrl ? `${apiBaseUrl}${path}` : path;
}

async function request(path, payload) {
  let response;

  try {
    response = await fetch(getApiUrl(path), {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
  } catch (error) {
    throw new Error(
      `Unable to reach the API at ${getApiUrl(path)}. Check the Render service URL and CORS settings.`,
    );
  }

  if (!response.ok) {
    const responseText = await response.text();
    const errorMessage = responseText.trim() || response.statusText || "Unknown error";
    throw new Error(
      path === "/api/review"
        ? `Unable to submit review. ${errorMessage}`
        : `Unable to load recommendations. ${errorMessage}`,
    );
  }

  return response.json();
}

export function fetchRecommendations(payload) {
  return request("/api/profile", payload);
}

export function submitReview(payload) {
  return request("/api/review", payload);
}
