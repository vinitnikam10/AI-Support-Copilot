import { useState } from "react";
import ResultCard from "./ResultCard";

function CollapsibleTicket({ text, index }) {
  const [open, setOpen] = useState(false);
  const isLong = text.length > 120;
  const preview = isLong ? text.slice(0, 120).trimEnd() + "..." : text;

  return (
    <button
      type="button"
      onClick={() => isLong && setOpen(!open)}
      className={`
        w-full text-left p-3 rounded-lg
        bg-slate-50 hover:bg-slate-100
        border border-slate-200/80
        transition-colors
        ${isLong ? "cursor-pointer" : "cursor-default"}
      `}
    >
      <div className="flex items-start gap-3">
        <span className="text-xs font-mono text-slate-400 mt-0.5">{index + 1}.</span>
        <span className="text-sm text-slate-700 leading-relaxed flex-1">
          {open ? text : preview}
        </span>
        {isLong && (
          <svg
            className={`w-4 h-4 text-slate-400 flex-shrink-0 transition-transform ${open ? "rotate-180" : ""}`}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <polyline points="6 9 12 15 18 9" />
          </svg>
        )}
      </div>
    </button>
  );
}

export default function SimilarTickets({ tickets }) {
  return (
    <ResultCard
      title="Similar Past Tickets"
      icon={
        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <circle cx="11" cy="11" r="8" />
          <line x1="21" y1="21" x2="16.65" y2="16.65" />
        </svg>
      }
    >
      {!tickets || tickets.length === 0 ? (
        <p className="text-sm text-slate-400 italic">
          No similar tickets found in the knowledge base.
        </p>
      ) : (
        <div className="flex flex-col gap-2">
          {tickets.map((t, i) => (
            <CollapsibleTicket key={i} text={t} index={i} />
          ))}
        </div>
      )}
    </ResultCard>
  );
}
