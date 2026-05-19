import { useState } from "react";
import Markdown from "markdown-to-jsx";
import ResultCard from "./ResultCard";

// Markdown rendering matched to the reply context (longer-form text).
const MARKDOWN_OPTIONS = {
  overrides: {
    p: { props: { className: "text-sm leading-relaxed text-slate-800 mb-3 last:mb-0" } },
    strong: { props: { className: "font-semibold text-slate-900" } },
    em: { props: { className: "italic" } },
    ul: { props: { className: "list-disc pl-5 space-y-1 text-sm text-slate-800 mb-3 last:mb-0" } },
    ol: { props: { className: "list-decimal pl-5 space-y-1 text-sm text-slate-800 mb-3 last:mb-0" } },
    li: { props: { className: "leading-relaxed" } },
    code: {
      props: { className: "px-1.5 py-0.5 rounded bg-slate-100 text-slate-800 text-[0.85em] font-mono" },
    },
    h1: { props: { className: "text-base font-semibold text-slate-900 mb-2" } },
    h2: { props: { className: "text-base font-semibold text-slate-900 mb-2" } },
    h3: { props: { className: "text-sm font-semibold text-slate-900 mb-2" } },
  },
};

export default function SuggestedReply({ reply }) {
  const [copied, setCopied] = useState(false);

  if (!reply) return null;

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(reply);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  return (
    <ResultCard
      title="Suggested Reply"
      icon={
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
      }
    >
      <div className="relative">
        <div className="p-4 rounded-lg bg-slate-50 border border-slate-200/80 pr-16">
          <Markdown options={MARKDOWN_OPTIONS}>{reply}</Markdown>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="
            absolute top-2 right-2 px-2.5 py-1 rounded
            text-xs font-medium
            bg-white hover:bg-slate-100
            text-slate-600 hover:text-slate-900
            border border-slate-200
            transition-colors
          "
        >
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
    </ResultCard>
  );
}
