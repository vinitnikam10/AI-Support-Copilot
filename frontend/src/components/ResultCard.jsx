/**
 * Reusable card wrapper for result sections (Summary, Classification, etc.).
 * Keeps spacing, borders, and animations consistent across cards.
 */
export default function ResultCard({ title, icon, children }) {
  return (
    <section
      className="
        bg-white border border-slate-200/80 rounded-xl p-5
        shadow-[0_1px_2px_rgba(15,23,42,0.04),0_1px_3px_rgba(15,23,42,0.03)]
        animate-fade-in
      "
    >
      <header className="flex items-center gap-2 mb-3">
        {icon && <span className="text-slate-400">{icon}</span>}
        <h3 className="text-[13px] font-semibold text-slate-500 tracking-wide">
          {title}
        </h3>
      </header>
      <div className="text-slate-800">{children}</div>
    </section>
  );
}
