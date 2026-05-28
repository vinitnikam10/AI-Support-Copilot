import Markdown from "markdown-to-jsx";
import ResultCard from "./ResultCard";

// Style overrides for markdown elements so they fit the card aesthetic
// instead of using browser defaults.
const MARKDOWN_OPTIONS = {
  overrides: {
    p: {
      props: { className: "text-sm leading-relaxed text-slate-700 mb-3 last:mb-0" },
    },
    strong: {
      props: { className: "font-semibold text-slate-900" },
    },
    ul: {
      props: { className: "list-disc pl-5 space-y-1 text-sm text-slate-700 mb-3 last:mb-0" },
    },
    ol: {
      props: { className: "list-decimal pl-5 space-y-1 text-sm text-slate-700 mb-3 last:mb-0" },
    },
    li: { props: { className: "leading-relaxed" } },
    code: {
      props: { className: "px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 text-[0.85em] font-mono" },
    },
  },
};

export default function SummaryCard({ summary }) {
  if (!summary) return null;

  return (
    <ResultCard
      title="Summary"
      icon={
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
          <polyline points="14 2 14 8 20 8" />
          <line x1="8" y1="13" x2="16" y2="13" />
          <line x1="8" y1="17" x2="13" y2="17" />
        </svg>
      }
    >
      <Markdown options={MARKDOWN_OPTIONS}>{summary}</Markdown>
    </ResultCard>
  );
}
