import { useEffect, useRef, useState } from "react";

import HomeView from "./components/HomeView";
import RecommendationView from "./components/RecommendationView";
import ReviewView from "./components/ReviewView";
import { THEME_CONFIG } from "./constants";
import { fetchRecommendations, submitReview } from "./lib/api";

const defaultProfileValues = {
  skin_type: "combination",
  concerns: [],
  budget: "50",
  preferences: "",
};

const defaultReviewValues = {
  review_category: "moisturizer",
  review_text: "",
  review_skin_type: "combination",
  review_rating: "4.0",
};

const agentStepTemplates = [
  {
    key: "goal_understanding",
    title: "Goal Understanding",
    summary: "Analyzing your skin profile, category, and preferences...",
  },
  {
    key: "data_retrieval",
    title: "Data Retrieval",
    summary: "Collecting review evidence for the selected category...",
  },
  {
    key: "filtering",
    title: "Filtering",
    summary: "Removing suspicious or promotional reviews...",
  },
  {
    key: "ranking",
    title: "Ranking",
    summary: "Scoring products with concern, rating, and trust signals...",
  },
  {
    key: "decision",
    title: "Decision",
    summary: "Choosing the strongest product and weighing trade-offs...",
  },
];

function buildLoadingSteps(activeIndex = 0) {
  return agentStepTemplates.map((step, index) => ({
    ...step,
    status: index < activeIndex ? "completed" : index === activeIndex ? "active" : "pending",
    details: [],
    metrics: {},
  }));
}

function getThemeKey(category, fallback = "default") {
  return THEME_CONFIG[category] ? category : fallback;
}

export default function App() {
  const [activeView, setActiveView] = useState("home");
  const [selectedCategory, setSelectedCategory] = useState("");
  const [profileValues, setProfileValues] = useState(defaultProfileValues);
  const [reviewValues, setReviewValues] = useState(defaultReviewValues);
  const [status, setStatus] = useState(
    "Choose a category and submit your profile to see recommendations.",
  );
  const [reviewStatus, setReviewStatus] = useState("Your review helps others.");
  const [loading, setLoading] = useState(false);
  const [agentSteps, setAgentSteps] = useState([]);
  const [recommendationData, setRecommendationData] = useState(null);
  const progressIntervalRef = useRef(null);

  useEffect(() => () => {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
    }
  }, []);

  const themeKey =
    activeView === "recommend"
      ? getThemeKey(selectedCategory, "default")
      : activeView === "review"
        ? getThemeKey(reviewValues.review_category, "default")
        : "default";

  const theme = THEME_CONFIG[themeKey];

  const pageStyle = {
    "--accent": theme.accent,
    "--accent-strong": theme.accentStrong,
    "--accent-soft": theme.accentSoft,
    "--border": "rgba(217, 200, 206, 0.72)",
    "--text": "#3c3340",
    "--muted": "#7e7280",
    background: `radial-gradient(circle at top left, ${theme.glow}, transparent 34%), radial-gradient(circle at 85% 20%, rgba(255, 255, 255, 0.9), transparent 28%), linear-gradient(180deg, ${theme.bgTop} 0%, ${theme.bgBottom} 100%)`,
  };

  function clearAgentProgress() {
    if (progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
  }

  function handleOpenRecommendations() {
    setActiveView("recommend");
  }

  function handleOpenReview() {
    setActiveView("review");
  }

  function handleBackHome() {
    setActiveView("home");
  }

  function handleSelectCategory(category) {
    setSelectedCategory(category);
    setStatus(`Selected ${category.charAt(0).toUpperCase() + category.slice(1)}. Complete your profile to see the best match.`);
    setLoading(false);
    setAgentSteps([]);
    setRecommendationData(null);
    clearAgentProgress();
  }

  function handleBackToCategory() {
    setSelectedCategory("");
    setProfileValues(defaultProfileValues);
    setStatus("Choose a category and submit your profile to see recommendations.");
    setLoading(false);
    setAgentSteps([]);
    setRecommendationData(null);
    clearAgentProgress();
  }

  function handleProfileChange(event) {
    const { name, value } = event.target;
    setProfileValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  function handleConcernToggle(value) {
    setProfileValues((current) => {
      const concerns = current.concerns.includes(value)
        ? current.concerns.filter((item) => item !== value)
        : [...current.concerns, value];

      return {
        ...current,
        concerns,
      };
    });
  }

  async function handleSubmitProfile(event) {
    event.preventDefault();

    const payload = {
      category: selectedCategory,
      skin_type: profileValues.skin_type,
      concerns: profileValues.concerns,
      budget: Number(profileValues.budget),
      preferences: profileValues.preferences.trim() || null,
    };

    clearAgentProgress();
    setStatus("The agent is reviewing your profile and building a decision...");
    setLoading(true);
    setAgentSteps(buildLoadingSteps(0));
    setRecommendationData(null);

    progressIntervalRef.current = setInterval(() => {
      setAgentSteps((current) => {
        if (!current.length) {
          return buildLoadingSteps(0);
        }

        const activeIndex = current.findIndex((step) => step.status === "active");

        if (activeIndex === -1 || activeIndex >= agentStepTemplates.length - 1) {
          return current.map((step, index) => ({
            ...step,
            status: index === agentStepTemplates.length - 1 ? "active" : "completed",
          }));
        }

        return buildLoadingSteps(activeIndex + 1);
      });
    }, 900);

    try {
      const data = await fetchRecommendations(payload);
      clearAgentProgress();
      setAgentSteps(data.agent_steps || []);
      setStatus(
        data.final_decision?.chosen_product
          ? `Decision complete. ${data.final_decision.chosen_product.label} is the agent's recommended product.`
          : data.final_decision?.reasoning || "No recommendations were found for that profile yet.",
      );
      setRecommendationData(data);
    } catch (error) {
      clearAgentProgress();
      setStatus(`Request failed: ${error.message}`);
      setAgentSteps([]);
      setRecommendationData(null);
    } finally {
      setLoading(false);
    }
  }

  function handleReviewChange(event) {
    const { name, value } = event.target;
    setReviewValues((current) => ({
      ...current,
      [name]: value,
    }));
  }

  async function handleSubmitReview(event) {
    event.preventDefault();

    const payload = {
      category: reviewValues.review_category,
      review_text: reviewValues.review_text.trim(),
      skin_type: reviewValues.review_skin_type,
      rating: Number(reviewValues.review_rating),
    };

    setReviewStatus("Saving your review...");

    try {
      const data = await submitReview(payload);
      setReviewStatus(
        `${data.message} Keywords: ${data.keywords.join(", ") || "none"}. Ad flag: ${data.is_ad}.`,
      );
      setReviewValues(defaultReviewValues);
    } catch (error) {
      setReviewStatus(`Review submission failed: ${error.message}`);
    }
  }

  return (
    <main
      className="relative min-h-screen overflow-hidden px-4 py-7 font-sans text-[var(--text)] transition-[background] duration-500 md:px-4 md:py-12"
      style={pageStyle}
    >
      <div className="pointer-events-none absolute left-[-80px] top-14 h-[280px] w-[280px] rounded-full bg-[rgba(255,223,235,0.55)] blur-md" />
      <div className="pointer-events-none absolute bottom-12 right-[-110px] h-[300px] w-[300px] rounded-full bg-[rgba(255,248,224,0.64)] blur-md" />
      <div
        className="pointer-events-none absolute inset-0"
        style={{
          background:
            "linear-gradient(120deg, rgba(255, 255, 255, 0.25), transparent 45%), radial-gradient(circle at 20% 80%, rgba(255, 255, 255, 0.22), transparent 25%)",
        }}
      />

      <div className="relative z-10 mx-auto grid min-h-[calc(100vh-56px)] w-full max-w-[980px] place-items-center">
        <div className="w-full">
          <div className={`transition duration-300 ${activeView === "home" ? "block opacity-100 translate-y-0" : "hidden opacity-0 translate-y-5"}`}>
            <HomeView
              onOpenRecommendations={handleOpenRecommendations}
              onOpenReview={handleOpenReview}
            />
          </div>

          <div className={`transition duration-300 ${activeView === "recommend" ? "block opacity-100 translate-y-0" : "hidden opacity-0 translate-y-5"}`}>
            <RecommendationView
              selectedCategory={selectedCategory}
              selectedThemeLabel={theme.label}
              status={status}
              loading={loading}
              agentSteps={agentSteps}
              recommendationData={recommendationData}
              profileValues={profileValues}
              onBackHome={handleBackHome}
              onSelectCategory={handleSelectCategory}
              onBackToCategory={handleBackToCategory}
              onProfileChange={handleProfileChange}
              onConcernToggle={handleConcernToggle}
              onSubmitProfile={handleSubmitProfile}
            />
          </div>

          <div className={`transition duration-300 ${activeView === "review" ? "block opacity-100 translate-y-0" : "hidden opacity-0 translate-y-5"}`}>
            <ReviewView
              selectedThemeLabel={theme.reviewLabel}
              reviewValues={reviewValues}
              reviewStatus={reviewStatus}
              onBackHome={handleBackHome}
              onReviewChange={handleReviewChange}
              onSubmitReview={handleSubmitReview}
            />
          </div>
        </div>
      </div>
    </main>
  );
}
