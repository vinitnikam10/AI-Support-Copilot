import { useState } from "react";

import TicketInput from "../components/TicketInput";
import SummaryCard from "../components/SummaryCard";
import ClassificationCard from "../components/ClassificationCard";
import SuggestedReply from "../components/SuggestedReply";
import SimilarTickets from "../components/SimilarTickets";
import { analyzeTicket } from "../api/apiClient";

export default function TicketPage() {

  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleAnalyze = async (ticketText) => {

    setLoading(true);

    try {

      const data = await analyzeTicket(ticketText);

      setResult(data);

    } catch (error) {

      console.error(error);
      alert("Error analyzing ticket");

    }

    setLoading(false);
  };

  return (

    <div style={{ maxWidth: "800px", margin: "auto", padding: "40px" }}>

      <h1>AI Support Copilot</h1>

      <TicketInput onAnalyze={handleAnalyze} />

      {loading && <p>Analyzing ticket...</p>}

      {result && (
        <>
          <SummaryCard summary={result.summary} />
          <ClassificationCard category={result.category} />
          <SimilarTickets tickets={result.similar_tickets} />
          <SuggestedReply reply={result.suggested_reply} />
        </>
      )}

    </div>
  );
}