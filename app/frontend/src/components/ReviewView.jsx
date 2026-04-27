import { CATEGORY_OPTIONS, SKIN_TYPE_OPTIONS } from "../constants";
import SectionHeader from "./SectionHeader";
import SurfaceCard from "./SurfaceCard";

function FieldLabel({ children, htmlFor }) {
  return (
    <label className="grid gap-2.5 text-[0.95rem] font-semibold text-[var(--text)]" htmlFor={htmlFor}>
      {children}
    </label>
  );
}

function InputBase({ as = "input", className = "", ...props }) {
  const Component = as;

  return (
    <Component
      className={`w-full rounded-xl border border-[#ddd5dc] bg-[#fffdfd] px-4 py-[14px] text-[var(--text)] outline-none transition duration-200 placeholder:text-[var(--muted)] focus:border-[var(--accent-strong)] focus:bg-white focus:ring-4 focus:ring-[var(--accent-soft)] ${className}`}
      {...props}
    />
  );
}

export default function ReviewView({
  selectedThemeLabel,
  reviewValues,
  reviewStatus,
  onBackHome,
  onReviewChange,
  onSubmitReview,
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
          Submit Review
        </p>
        <h1 className="font-display text-[3rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)] md:text-[4rem]">
          Share Your Experience
        </h1>
        <p className="mt-3 text-base leading-7 text-[var(--muted)]">
          Your review helps others make better beauty decisions.
        </p>

        <SurfaceCard>
          <SectionHeader
            step="+"
            title="Tell us how it worked for your skin"
            description="Helpful details make future recommendations stronger."
          />

          <form className="mt-[22px] grid gap-[18px]" onSubmit={onSubmitReview}>
            <FieldLabel htmlFor="review_category">
              <span>Product category</span>
              <select
                id="review_category"
                name="review_category"
                value={reviewValues.review_category}
                onChange={onReviewChange}
                className="w-full rounded-xl border border-[#ddd5dc] bg-[#fffdfd] px-4 py-[14px] text-[var(--text)] outline-none transition duration-200 focus:border-[var(--accent-strong)] focus:bg-white focus:ring-4 focus:ring-[var(--accent-soft)]"
              >
                {CATEGORY_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.title}
                  </option>
                ))}
              </select>
            </FieldLabel>

            <FieldLabel htmlFor="review_text">
              <span>Your review</span>
              <InputBase
                as="textarea"
                id="review_text"
                name="review_text"
                rows="5"
                required
                value={reviewValues.review_text}
                onChange={onReviewChange}
                placeholder="Share what worked, what did not, and who you think this product is best for."
                className="min-h-[140px] resize-y leading-7"
              />
            </FieldLabel>

            <div className="grid gap-[18px] md:grid-cols-2">
              <FieldLabel htmlFor="review_skin_type">
                <span>Skin type</span>
                <select
                  id="review_skin_type"
                  name="review_skin_type"
                  value={reviewValues.review_skin_type}
                  onChange={onReviewChange}
                  className="w-full rounded-xl border border-[#ddd5dc] bg-[#fffdfd] px-4 py-[14px] text-[var(--text)] outline-none transition duration-200 focus:border-[var(--accent-strong)] focus:bg-white focus:ring-4 focus:ring-[var(--accent-soft)]"
                >
                  {SKIN_TYPE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </FieldLabel>

              <FieldLabel htmlFor="review_rating">
                <span>Rating</span>
                <InputBase
                  id="review_rating"
                  type="number"
                  name="review_rating"
                  min="0"
                  max="5"
                  step="0.1"
                  required
                  value={reviewValues.review_rating}
                  onChange={onReviewChange}
                />
              </FieldLabel>
            </div>

            <button
              type="submit"
              className="rounded-2xl px-5 py-3.5 font-bold text-white shadow-[0_14px_30px_rgba(180,130,150,0.2)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
              style={{
                background:
                  "linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%)",
              }}
            >
              Submit review
            </button>
          </form>

          <p className="mt-[18px] inline-flex rounded-full border border-[var(--border)] bg-white/80 px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--text)]">
            {reviewStatus}
          </p>
        </SurfaceCard>
      </div>
    </section>
  );
}
