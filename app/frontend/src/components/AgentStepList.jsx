export default function AgentStepList({ steps }) {
  if (!steps.length) {
    return null;
  }

  return (
    <section className="mt-6">
      <p className="text-xs font-bold uppercase tracking-[0.22em] text-[var(--accent-strong)]">
        Agent Steps
      </p>
      <h3 className="mt-1 font-display text-[1.8rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)]">
        Decision trace
      </h3>

      <div className="mt-4 grid gap-3">
        {steps.map((step, index) => {
          const statusClass =
            step.status === "active"
              ? "border-[var(--accent-strong)] bg-[var(--accent-soft)]"
              : step.status === "completed"
                ? "border-[#e4dbe1] bg-white"
                : "border-[#eee6eb] bg-[#fcfafb]";

          const dotClass =
            step.status === "active"
              ? "bg-[var(--accent-strong)]"
              : step.status === "completed"
                ? "bg-emerald-500"
                : "bg-[#d8ced5]";

          return (
            <article
              key={step.key}
              className={`rounded-2xl border px-5 py-4 shadow-soft transition duration-200 ${statusClass}`}
            >
              <div className="flex flex-col gap-3 md:flex-row md:items-start md:justify-between">
                <div className="flex items-start gap-3">
                  <span className={`mt-1 h-3 w-3 shrink-0 rounded-full ${dotClass}`} />
                  <div>
                    <p className="text-[0.8rem] font-bold uppercase tracking-[0.16em] text-[var(--muted)]">
                      {`Step ${index + 1}`}
                    </p>
                    <h4 className="mt-1 text-lg font-semibold text-[var(--text)]">
                      {step.title}
                    </h4>
                    <p className="mt-1 text-[15px] leading-7 text-[var(--muted)]">
                      {step.summary}
                    </p>
                  </div>
                </div>

                <span className="inline-flex rounded-full border border-[var(--border)] bg-white/85 px-3 py-2 text-[0.82rem] font-semibold capitalize text-[var(--text)]">
                  {step.status}
                </span>
              </div>

              {step.details?.length ? (
                <div className="mt-4 grid gap-2">
                  {step.details.map((detail) => (
                    <div
                      key={`${step.key}-${detail}`}
                      className="rounded-xl bg-white/80 px-4 py-3 text-[14px] leading-6 text-[var(--text)]"
                    >
                      {detail}
                    </div>
                  ))}
                </div>
              ) : null}

              {Object.keys(step.metrics || {}).length ? (
                <div className="mt-4 flex flex-wrap gap-2.5">
                  {Object.entries(step.metrics).map(([metricKey, value]) => (
                    <span
                      key={`${step.key}-${metricKey}`}
                      className="rounded-full bg-[#fbf8fa] px-3 py-2 text-[0.84rem] font-medium text-[var(--muted)]"
                    >
                      {`${metricKey.replace(/_/g, " ")}: ${value}`}
                    </span>
                  ))}
                </div>
              ) : null}
            </article>
          );
        })}
      </div>
    </section>
  );
}
