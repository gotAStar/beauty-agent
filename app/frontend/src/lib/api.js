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
  const response = await fetch(getApiUrl(path), {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error(path === "/api/review" ? "Unable to submit review." : "Unable to load recommendations.");
  }

  return response.json();
}

export function fetchRecommendations(payload) {
  return request("/api/profile", payload);
}

export function submitReview(payload) {
  return request("/api/review", payload);
}
