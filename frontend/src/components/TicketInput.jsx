import { useEffect, useRef, useState } from "react";
import MicButton from "./MicButton";

export default function TicketInput({ onAnalyze, loading }) {
  const [ticketText, setTicketText] = useState("");
  const textareaRef = useRef(null);

  // Auto-grow the textarea up to a max height.
  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 240)}px`;
  }, [ticketText]);

  const handleSubmit = () => {
    if (!ticketText.trim() || loading) return;
    onAnalyze(ticketText);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleTranscript = (transcript) => {
    setTicketText((prev) => (prev ? `${prev} ${transcript}` : transcript));
  };

  const canSubmit = ticketText.trim().length > 0 && !loading;

  return (
    <div className="relative">
      <div
        className="
          flex flex-col gap-2 p-3 rounded-2xl
          bg-white border border-slate-200/80
          shadow-[0_1px_2px_rgba(15,23,42,0.04),0_1px_3px_rgba(15,23,42,0.03)]
          focus-within:border-slate-300 focus-within:shadow-[0_2px_8px_rgba(15,23,42,0.06)]
          transition-all
        "
      >
        <textarea
          ref={textareaRef}
          rows={3}
          placeholder="Paste a support ticket or Slack message, or use the mic to dictate..."
          value={ticketText}
          onChange={(e) => setTicketText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={loading}
          className="
            w-full bg-transparent text-slate-900 placeholder-slate-400
            resize-none outline-none px-2 py-1.5
            disabled:opacity-50
          "
        />

        <div className="flex items-center justify-between gap-3 px-1">
          <MicButton onTranscript={handleTranscript} disabled={loading} />

          <div className="flex items-center gap-3">
            <span className="text-xs text-slate-400 hidden sm:inline">
              {ticketText.length > 0 && `${ticketText.length} chars · ⌘+Enter to submit`}
            </span>
            <button
              type="button"
              onClick={handleSubmit}
              disabled={!canSubmit}
              className="
                px-4 py-2 rounded-lg font-medium text-sm
                bg-slate-900 text-white
                hover:bg-slate-800 active:bg-slate-950
                disabled:bg-slate-200 disabled:text-slate-400 disabled:cursor-not-allowed
                transition-colors
              "
            >
              {loading ? "Analyzing..." : "Analyze Ticket"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
