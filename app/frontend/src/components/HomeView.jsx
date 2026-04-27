export default function HomeView({ onOpenRecommendations, onOpenReview }) {
  return (
    <section className="opacity-100 transition duration-300">
      <div className="rounded-[28px] border border-white/70 bg-white/80 px-7 py-14 text-center shadow-shell backdrop-blur-[20px]">
        <p className="mb-2.5 text-xs font-bold uppercase tracking-[0.22em] text-[var(--accent-strong)]">
          Beauty Decision Assistant
        </p>
        <h1 className="mx-auto mb-3 max-w-4xl font-display text-[3rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)] md:text-[4.75rem]">
          Beauty picks that feel personal, calm, and trustworthy.
        </h1>
        <p className="mx-auto max-w-[680px] text-base leading-7 text-[var(--muted)]">
          Discover skincare recommendations built around your skin profile,
          real review signals, and a cleaner review set.
        </p>

        <div className="mx-auto mt-8 grid max-w-[620px] gap-4 md:grid-cols-2">
          <button
            type="button"
            onClick={onOpenRecommendations}
            className="rounded-2xl px-6 py-[22px] text-[1.05rem] font-bold text-white shadow-[0_14px_30px_rgba(180,130,150,0.2)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
            style={{
              background:
                "linear-gradient(135deg, var(--accent) 0%, var(--accent-strong) 100%)",
            }}
          >
            Get Recommendation
          </button>
          <button
            type="button"
            onClick={onOpenReview}
            className="rounded-2xl border border-[var(--border)] bg-white/90 px-6 py-[22px] text-[1.05rem] font-bold text-[var(--text)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
          >
            Submit Review
          </button>
        </div>

        <div className="mt-[22px] flex flex-wrap items-center justify-center gap-2.5 text-[0.95rem] text-[var(--muted)]">
          <span>✔ Personalized matching</span>
          <span>⭐ Explainable ranking</span>
          <span>❌ Ad filtering</span>
        </div>
      </div>
    </section>
  );
}
