import { useState } from "react";

import TicketInput from "../components/TicketInput";
import SummaryCard from "../components/SummaryCard";
import ClassificationCard from "../components/ClassificationCard";
import SimilarTickets from "../components/SimilarTickets";
import SuggestedReply from "../components/SuggestedReply";
import SkeletonResults from "../components/SkeletonResults";
import { analyzeTicket } from "../api/apiClient";

export default function TicketPage() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (ticketText) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await analyzeTicket(ticketText);
      setResult(data);
    } catch (err) {
      console.error(err);
      const detail = err?.response?.data?.detail;
      setError(detail || "Failed to analyze the ticket. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <main className="max-w-3xl mx-auto px-4 sm:px-6 py-10">
        <header className="mb-8 animate-fade-in">
          <h1 className="text-3xl font-semibold tracking-tight text-slate-900">
            AI Support Copilot
          </h1>
          <p className="mt-1.5 text-sm text-slate-500">
            Summarize, classify, and draft replies for healthcare EMR & billing tickets.
          </p>
        </header>

        <TicketInput onAnalyze={handleAnalyze} loading={loading} />

        <div className="mt-6 flex flex-col gap-4">
          {error && (
            <div className="rounded-lg p-4 bg-red-50 border border-red-200 text-red-700 text-sm animate-fade-in">
              {error}
            </div>
          )}

          {loading && <SkeletonResults />}

          {result && !loading && (
            <>
              <SummaryCard summary={result.summary} />
              <ClassificationCard
                majorCategory={result.major_category}
                subCategory={result.sub_category}
              />
              <SimilarTickets tickets={result.similar_tickets} />
              <SuggestedReply reply={result.suggested_reply} />
            </>
          )}
        </div>
      </main>
    </div>
  );
}
