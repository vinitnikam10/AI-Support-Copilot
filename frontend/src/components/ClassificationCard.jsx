import ResultCard from "./ResultCard";

export default function ClassificationCard({ majorCategory, subCategory }) {
  if (!majorCategory) return null;

  return (
    <ResultCard
      title="Category"
      icon={
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M20.59 13.41l-7.17 7.17a2 2 0 0 1-2.83 0L2 12V2h10l8.59 8.59a2 2 0 0 1 0 2.82z" />
          <line x1="7" y1="7" x2="7.01" y2="7" />
        </svg>
      }
    >
      <div className="flex items-center gap-2 text-sm">
        <span className="px-2.5 py-1 rounded-md bg-slate-100 text-slate-700 font-medium border border-slate-200">
          {majorCategory}
        </span>
        <svg className="w-3.5 h-3.5 text-slate-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="px-2.5 py-1 rounded-md bg-white text-slate-700 font-medium border border-slate-200">
          {subCategory}
        </span>
      </div>
    </ResultCard>
  );
}
