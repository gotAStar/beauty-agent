import { buildSignalItems, formatCategory } from "../utils/recommendations";

const toneClassMap = {
  positive: "text-emerald-600",
  negative: "text-rose-500",
  neutral: "text-[var(--accent-strong)]",
};

const classificationStyles = {
  "Hidden gem": "bg-emerald-50 text-emerald-700 border-emerald-200",
  "Trending but risky": "bg-amber-50 text-amber-700 border-amber-200",
  "Balanced choice": "bg-[#fbf8fa] text-[var(--text)] border-[#ece3e8]",
};

export default function RecommendationCard({
  recommendation,
  index,
  trustScore,
  eyebrowLabel,
}) {
  const signals = buildSignalItems(recommendation);
  const cardBorderClass =
    recommendation.product_classification === "Hidden gem"
      ? "border-emerald-300"
      : recommendation.product_classification === "Trending but risky"
        ? "border-amber-300"
        : "border-[#eae2e7]";

  return (
    <article
      className={`animate-card-in rounded-[20px] border bg-white p-6 shadow-soft ${cardBorderClass}`}
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className="mb-4 flex flex-col items-start justify-between gap-[18px] md:flex-row">
        <div>
          <span className="mb-2 inline-block text-[0.82rem] font-extrabold uppercase tracking-[0.16em] text-[var(--accent-strong)]">
            {eyebrowLabel || `Top ${index + 1}`}
          </span>
          <h3 className="font-display text-[1.95rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)]">
            {recommendation.label}
          </h3>
          <p className="mt-3 flex flex-wrap gap-2.5 text-[0.92rem] text-[var(--muted)]">
            <span className={`rounded-full border px-2.5 py-2 font-semibold ${classificationStyles[recommendation.product_classification] || classificationStyles["Balanced choice"]}`}>
              {recommendation.product_classification}
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {formatCategory(recommendation.category)}
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {`ASIN ${recommendation.asin}`}
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {formatCategory(recommendation.skin_type)} skin
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {recommendation.rating.toFixed(1)} rating
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {`${recommendation.review_count} reviews`}
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {`Promotion ${Math.round(recommendation.promotion_score * 100)}%`}
            </span>
            <span className="rounded-full bg-[#fbf8fa] px-2.5 py-2">
              {`Consistency ${recommendation.consistency_score}/100`}
            </span>
          </p>
        </div>

        <div
          className="inline-flex rounded-2xl px-[14px] py-3 font-extrabold text-[var(--accent-strong)]"
          style={{
            background:
              "linear-gradient(135deg, var(--accent-soft), rgba(255, 255, 255, 0.96))",
          }}
        >
          {`Trust ${trustScore}/100`}
        </div>
      </div>

      <div className="mt-[18px] grid gap-3">
        {recommendation.marketing_bias_warning ? (
          <div className="rounded-2xl border border-amber-200 bg-amber-50 px-[14px] py-3 text-[14px] leading-6 text-amber-800">
            {recommendation.marketing_bias_warning}
          </div>
        ) : null}
        {recommendation.product_classification === "Hidden gem" ? (
          <div className="rounded-2xl border border-emerald-200 bg-emerald-50 px-[14px] py-3 text-[14px] leading-6 text-emerald-800">
            Hidden gem: low marketing pressure with strong agreement across reviews.
          </div>
        ) : null}
        {signals.map((signal) => (
          <div
            key={`${recommendation.asin}-${signal.icon}-${signal.text}`}
            className="grid grid-cols-[24px_1fr] items-start gap-3 rounded-2xl bg-[#fcfafb] px-[14px] py-3"
          >
            <span className={`text-base leading-6 ${toneClassMap[signal.tone]}`}>
              {signal.icon}
            </span>
            <span className="text-[15px] leading-7 text-[var(--text)]">
              {signal.text}
            </span>
          </div>
        ))}
      </div>

      <div className="mt-[18px] flex flex-col items-start justify-between gap-[18px] md:flex-row">
        <span className="inline-flex rounded-full border border-[var(--border)] bg-white/80 px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--text)]">
          {`Score ${recommendation.score.toFixed(1)}`}
        </span>
        <div className="flex flex-wrap items-center gap-3">
          <span className="inline-flex rounded-full border border-[var(--border)] bg-white/80 px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--muted)]">
            {`Ad signal ${recommendation.ad_score.toFixed(2)}`}
          </span>
          {recommendation.amazon_url ? (
            <a
              href={recommendation.amazon_url}
              target="_blank"
              rel="noreferrer"
              className="inline-flex rounded-full border border-[var(--accent-strong)] bg-[var(--accent-soft)] px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--accent-strong)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
            >
              View on Amazon
            </a>
          ) : null}
        </div>
      </div>
    </article>
  );
}
