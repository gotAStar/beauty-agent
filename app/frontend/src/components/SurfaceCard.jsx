export default function SurfaceCard({ children, className = "", style }) {
  return (
    <section
      className={`mt-6 rounded-[20px] border border-white/70 bg-white p-6 shadow-soft ${className}`}
      style={style}
    >
      {children}
    </section>
  );
}
