import { buildSignalItems, formatCategory } from "../utils/recommendations";

const toneClassMap = {
  positive: "text-emerald-600",
  negative: "text-rose-500",
  neutral: "text-[var(--accent-strong)]",
};

export default function RecommendationCard({
  recommendation,
  index,
  trustScore,
}) {
  const signals = buildSignalItems(recommendation);

  return (
    <article
      className="animate-card-in rounded-[20px] border border-[#eae2e7] bg-white p-6 shadow-soft"
      style={{ animationDelay: `${index * 80}ms` }}
    >
      <div className="mb-4 flex flex-col items-start justify-between gap-[18px] md:flex-row">
        <div>
          <span className="mb-2 inline-block text-[0.82rem] font-extrabold uppercase tracking-[0.16em] text-[var(--accent-strong)]">
            {`Top ${index + 1}`}
          </span>
          <h3 className="font-display text-[1.95rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)]">
            {recommendation.label}
          </h3>
          <p className="mt-3 flex flex-wrap gap-2.5 text-[0.92rem] text-[var(--muted)]">
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

      <ul className="mt-[18px] grid gap-3">
        {signals.map((signal) => (
          <li
            key={`${recommendation.asin}-${signal.icon}-${signal.text}`}
            className="grid grid-cols-[24px_1fr] items-start gap-3 rounded-2xl bg-[#fcfafb] px-[14px] py-3"
          >
            <span className={`text-base leading-6 ${toneClassMap[signal.tone]}`}>
              {signal.icon}
            </span>
            <span className="text-[15px] leading-7 text-[var(--text)]">
              {signal.text}
            </span>
          </li>
        ))}
      </ul>

      <div className="mt-[18px] flex flex-col items-start justify-between gap-[18px] md:flex-row">
        <span className="inline-flex rounded-full border border-[var(--border)] bg-white/80 px-[14px] py-2.5 text-[0.92rem] font-semibold text-[var(--text)]">
          {`⭐ Score ${recommendation.score.toFixed(1)}`}
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
