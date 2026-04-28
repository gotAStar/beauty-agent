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

export default function DecisionSummaryCard({ finalDecision, trustScore }) {
  if (!finalDecision) {
    return null;
  }

  const chosenProduct = finalDecision.chosen_product;

  if (!chosenProduct) {
    return (
      <article className="mt-5 rounded-[24px] border border-[#e6dde3] bg-white p-6 shadow-soft">
        <p className="text-xs font-bold uppercase tracking-[0.22em] text-[var(--accent-strong)]">
          Final Decision
        </p>
        <h3 className="mt-2 font-display text-[2.1rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)]">
          No confident winner yet
        </h3>
        <p className="mt-4 text-base leading-7 text-[var(--muted)]">
          {finalDecision.reasoning}
        </p>

        {finalDecision.trade_offs?.length ? (
          <div className="mt-5 grid gap-3">
            {finalDecision.trade_offs.map((tradeOff) => (
              <div
                key={tradeOff}
                className="rounded-2xl bg-[#fcfafb] px-4 py-3 text-[15px] leading-7 text-[var(--text)]"
              >
                {tradeOff}
              </div>
            ))}
          </div>
        ) : null}
      </article>
    );
  }

  const signals = buildSignalItems(chosenProduct);
  const cardBorderClass =
    chosenProduct.product_classification === "Hidden gem"
      ? "border-emerald-300"
      : chosenProduct.product_classification === "Trending but risky"
        ? "border-amber-300"
        : "border-[var(--accent-strong)]";

  return (
    <article className={`mt-5 rounded-[24px] border bg-white p-6 shadow-[0_22px_55px_rgba(184,165,175,0.22)] ${cardBorderClass}`}>
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <p className="text-xs font-bold uppercase tracking-[0.22em] text-[var(--accent-strong)]">
            Final Decision
          </p>
          <h3 className="mt-2 font-display text-[2.4rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)]">
            {chosenProduct.label}
          </h3>
          <p className="mt-4 text-base leading-7 text-[var(--muted)]">
            {finalDecision.reasoning}
          </p>
        </div>

        <div className="grid gap-3">
          <span className="inline-flex rounded-2xl bg-[var(--accent-soft)] px-4 py-3 text-[0.95rem] font-extrabold text-[var(--accent-strong)]">
            {`Confidence ${finalDecision.confidence_score}/100`}
          </span>
          <span className="inline-flex rounded-2xl border border-[var(--border)] bg-white/90 px-4 py-3 text-[0.95rem] font-semibold text-[var(--text)]">
            {`Trust ${trustScore}/100`}
          </span>
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-2.5 text-[0.92rem] text-[var(--muted)]">
        <span className={`rounded-full border px-3 py-2 font-semibold ${classificationStyles[chosenProduct.product_classification] || classificationStyles["Balanced choice"]}`}>
          {chosenProduct.product_classification}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {formatCategory(chosenProduct.category)}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`ASIN ${chosenProduct.asin}`}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`${chosenProduct.rating.toFixed(1)} rating`}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`${chosenProduct.review_count} reviews`}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`${chosenProduct.score.toFixed(1)} score`}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`Promotion ${Math.round(chosenProduct.promotion_score * 100)}%`}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`Consistency ${chosenProduct.consistency_score}/100`}
        </span>
        <span className="rounded-full bg-[#fbf8fa] px-3 py-2">
          {`Hidden gem ${chosenProduct.hidden_gem_score}/100`}
        </span>
      </div>

      {chosenProduct.marketing_bias_warning ? (
        <div className="mt-5 rounded-2xl border border-amber-200 bg-amber-50 px-4 py-3 text-[15px] leading-7 text-amber-800">
          {chosenProduct.marketing_bias_warning}
        </div>
      ) : null}

      {chosenProduct.product_classification === "Hidden gem" ? (
        <div className="mt-5 rounded-2xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-[15px] leading-7 text-emerald-800">
          Hidden gem highlight: this product shows low promotion, high review agreement, and strong ratings.
        </div>
      ) : null}

      <div className="mt-6 grid gap-3">
        {signals.map((signal) => (
          <div
            key={`${chosenProduct.asin}-${signal.icon}-${signal.text}`}
            className="grid grid-cols-[24px_1fr] items-start gap-3 rounded-2xl bg-[#fcfafb] px-4 py-3"
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

      {finalDecision.trade_offs?.length ? (
        <section className="mt-6">
          <p className="text-xs font-bold uppercase tracking-[0.18em] text-[var(--accent-strong)]">
            Trade-offs
          </p>
          <div className="mt-3 grid gap-3">
            {finalDecision.trade_offs.map((tradeOff) => (
              <div
                key={tradeOff}
                className="rounded-2xl border border-[#ece3e8] bg-white px-4 py-3 text-[15px] leading-7 text-[var(--text)]"
              >
                {tradeOff}
              </div>
            ))}
          </div>
        </section>
      ) : null}

      {chosenProduct.amazon_url ? (
        <div className="mt-6">
          <a
            href={chosenProduct.amazon_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex rounded-full border border-[var(--accent-strong)] bg-[var(--accent-soft)] px-4 py-3 text-[0.95rem] font-semibold text-[var(--accent-strong)] transition duration-200 hover:-translate-y-0.5 hover:shadow-soft"
          >
            View on Amazon
          </a>
        </div>
      ) : null}
    </article>
  );
}
