import { CATEGORY_OPTIONS, CONCERN_OPTIONS, SKIN_TYPE_OPTIONS } from "../constants";
import { formatCategory } from "../utils/recommendations";
import RecommendationCard from "./RecommendationCard";
import SectionHeader from "./SectionHeader";
import SurfaceCard from "./SurfaceCard";

function FieldLabel({ children, htmlFor }) {
  return (
    <label className="grid gap-2.5 text-[0.95rem] font-semibold text-[var(--text)]" htmlFor={htmlFor}>
      {children}
    </label>
  );
}

function InputBase({ className = "", ...props }) {
  return (
    <input
      className={`w-full rounded-xl border border-[#ddd5dc] bg-[#fffdfd] px-4 py-[14px] text-[var(--text)] outline-none transition duration-200 placeholder:text-[var(--muted)] focus:border-[var(--accent-strong)] focus:bg-white focus:ring-4 focus:ring-[var(--accent-soft)] ${className}`}
      {...props}
    />
  );
}

function SelectBase(props) {
  return (
    <select
      className="w-full rounded-xl border border-[#ddd5dc] bg-[#fffdfd] px-4 py-[14px] text-[var(--text)] outline-none transition duration-200 focus:border-[var(--accent-strong)] focus:bg-white focus:ring-4 focus:ring-[var(--accent-soft)]"
      {...props}
    />
  );
}

export default function RecommendationView({
  selectedCategory,
  selectedThemeLabel,
  status,
  loading,
  recommendationData,
  profileValues,
  onBackHome,
  onSelectCategory,
  onBackToCategory,
  onProfileChange,
  onConcernToggle,
  onSubmitProfile,
}) {
  return (
    <section className="opacity-100 transition duration-300">
      <div className="rounded-[28px] border border-white/70 bg-white/80 p-7 shadow-shell backdrop-blur-[20px]">
        <div className="mb-[18px] flex flex-col items-start justify-between gap-3 md:flex-row">
          <button
            type="button"
            onClick={onBackHome}
            className="rounded-2xl border border-[var(--border)] bg-white/90 px-[18px] py-3 font-medium text-[var(--text)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
          >
            Back
          </button>
          <span className="inline-flex rounded-full border border-[var(--border)] bg-white/80 px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--text)]">
            {selectedThemeLabel}
          </span>
        </div>

        <p className="mb-2.5 text-xs font-bold uppercase tracking-[0.22em] text-[var(--accent-strong)]">
          Get Recommendation
        </p>
        <h1 className="font-display text-[3rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)] md:text-[4rem]">
          Find your next skincare match
        </h1>
        <p className="mt-3 text-base leading-7 text-[var(--muted)]">
          Start with a category, then share your skin profile for a more
          thoughtful top 3.
        </p>

        <SurfaceCard
          style={{
            background:
              "linear-gradient(135deg, var(--accent-soft) 0%, rgba(255, 255, 255, 0.96) 65%)",
          }}
        >
          <SectionHeader
            step="1"
            title="Choose a product category"
            description="Pick the area you want help with today."
          />

          <div className="mt-[22px] grid gap-[14px] md:grid-cols-3">
            {CATEGORY_OPTIONS.map((option) => {
              const isSelected = selectedCategory === option.value;

              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => onSelectCategory(option.value)}
                  className={`rounded-2xl border bg-white/95 px-[18px] py-5 text-left transition duration-200 hover:-translate-y-0.5 hover:shadow-soft ${
                    isSelected
                      ? "border-[var(--accent-strong)] shadow-[0_16px_34px_rgba(185,166,176,0.18)]"
                      : "border-[#e4dbe1]"
                  }`}
                  style={
                    isSelected
                      ? {
                          background:
                            "linear-gradient(135deg, var(--accent-soft), rgba(255, 255, 255, 0.98))",
                        }
                      : undefined
                  }
                >
                  <span className="mb-1.5 block text-base font-bold text-[var(--text)]">
                    {option.title}
                  </span>
                  <span className="block text-[0.93rem] leading-6 text-[var(--muted)]">
                    {option.copy}
                  </span>
                </button>
              );
            })}
          </div>
        </SurfaceCard>

        {selectedCategory ? (
          <SurfaceCard>
            <SectionHeader
              step="2"
              title="Complete your skin profile"
              description={`Selected category: ${formatCategory(selectedCategory)}`}
            />

            <form className="mt-[22px] grid gap-[18px]" onSubmit={onSubmitProfile}>
              <FieldLabel htmlFor="skin_type">
                <span>Skin type</span>
                <SelectBase
                  id="skin_type"
                  name="skin_type"
                  value={profileValues.skin_type}
                  onChange={onProfileChange}
                >
                  {SKIN_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </SelectBase>
              </FieldLabel>

              <fieldset className="grid gap-3">
                <legend className="text-[0.95rem] font-semibold text-[var(--text)]">
                  Concerns
                </legend>
                <div className="flex flex-wrap gap-2.5">
                  {CONCERN_OPTIONS.map((concern) => {
                    const checked = profileValues.concerns.includes(concern.value);

                    return (
                      <label
                        key={concern.value}
                        className="relative inline-flex cursor-pointer items-center"
                      >
                        <input
                          type="checkbox"
                          className="peer sr-only"
                          name="concerns"
                          value={concern.value}
                          checked={checked}
                          onChange={() => onConcernToggle(concern.value)}
                        />
                        <span className="inline-flex min-h-11 items-center justify-center rounded-full border border-[#dfd6dc] bg-white px-[14px] py-2.5 text-[15px] text-[var(--muted)] transition duration-200 peer-checked:-translate-y-px peer-checked:border-[var(--accent-strong)] peer-checked:bg-[var(--accent-soft)] peer-checked:text-[var(--text)]">
                          {concern.label}
                        </span>
                      </label>
                    );
                  })}
                </div>
              </fieldset>

              <div className="grid gap-[18px] md:grid-cols-2">
                <FieldLabel htmlFor="budget">
                  <span>Budget</span>
                  <InputBase
                    id="budget"
                    type="number"
                    name="budget"
                    min="0"
                    step="0.01"
                    value={profileValues.budget}
                    onChange={onProfileChange}
                  />
                </FieldLabel>

                <FieldLabel htmlFor="preferences">
                  <span>Preferences</span>
                  <InputBase
                    id="preferences"
                    type="text"
                    name="preferences"
                    placeholder="Fragrance-free, light texture, travel-friendly..."
                    value={profileValues.preferences}
                    onChange={onProfileChange}
                  />
                </FieldLabel>
              </div>

              <div className="grid gap-3 md:grid-cols-2">
                <button
                  type="button"
                  onClick={onBackToCategory}
                  className="w-full rounded-2xl border border-[var(--border)] bg-white/90 px-5 py-3.5 font-medium text-[var(--text)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
                >
                  Change category
                </button>
                <button
                  type="submit"
                  className="w-full rounded-2xl px-5 py-3.5 font-bold text-white shadow-[0_14px_30px_rgba(180,130,150,0.2)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
                  style={{
                    background:
                      "linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%)",
                  }}
                >
                  Get Recommendations
                </button>
              </div>
            </form>
          </SurfaceCard>
        ) : null}

        <section className="mt-[26px]">
          <div className="flex flex-col items-start justify-between gap-[18px] md:flex-row">
            <div>
              <p className="mb-2.5 text-xs font-bold uppercase tracking-[0.22em] text-[var(--accent-strong)]">
                Top 3 Picks
              </p>
              <h2 className="font-display text-[2rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)] md:text-[2.55rem]">
                Your recommendations
              </h2>
            </div>

            {recommendationData ? (
              <div className="inline-flex rounded-full border border-[var(--border)] bg-white/80 px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--text)]">
                {`Trust score ${recommendationData.trust_score}/100 • ${recommendationData.total_reviews_analyzed} reviews analyzed • ${recommendationData.filtered_reviews_count} filtered`}
              </div>
            ) : null}
          </div>

          <p className="mt-3 text-base leading-7 text-[var(--muted)]">{status}</p>

          {loading ? (
            <div className="mt-[18px] inline-flex items-center gap-3 rounded-full border border-[var(--border)] bg-white/90 px-4 py-3 text-[var(--muted)]">
              <span className="h-[18px] w-[18px] animate-spin-soft rounded-full border-2 border-black/10 border-t-[var(--accent-strong)]" />
              <span>Matching your concerns with trusted review signals...</span>
            </div>
          ) : null}

          {recommendationData ? (
            <div className="mt-[18px] grid gap-4">
              {recommendationData.recommendations.slice(0, 3).map((recommendation, index) => (
                <RecommendationCard
                  key={`${recommendation.product}-${index}`}
                  recommendation={recommendation}
                  index={index}
                  trustScore={recommendationData.trust_score}
                />
              ))}
            </div>
          ) : null}
        </section>
      </div>
    </section>
  );
}
