export default function SectionHeader({
  step,
  title,
  description,
  descriptionId,
}) {
  return (
    <div className="flex flex-col items-start gap-4 md:flex-row md:gap-[18px]">
      <span className="grid h-11 w-11 shrink-0 place-items-center rounded-[14px] bg-[var(--accent-soft)] text-base font-extrabold text-[var(--accent-strong)]">
        {step}
      </span>
      <div>
        <h2 className="font-display text-[2rem] leading-[0.95] tracking-[-0.02em] text-[var(--text)] md:text-[2.3rem]">
          {title}
        </h2>
        <p id={descriptionId} className="mt-2 text-[15px] leading-7 text-[var(--muted)]">
          {description}
        </p>
      </div>
    </div>
  );
}
