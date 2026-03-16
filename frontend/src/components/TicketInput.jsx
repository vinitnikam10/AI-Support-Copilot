import { useState } from "react";

export default function TicketInput({ onAnalyze }) {

  const [ticketText, setTicketText] = useState("");

  const handleSubmit = () => {
    if (!ticketText.trim()) return;

    onAnalyze(ticketText);
  };

  return (
    <div style={{ marginBottom: "30px" }}>
      <h2>Enter Support Ticket</h2>

      <textarea
        rows="6"
        style={{ width: "100%", padding: "10px" }}
        placeholder="Paste client support ticket or Slack message..."
        value={ticketText}
        onChange={(e) => setTicketText(e.target.value)}
      />

      <button
        style={{ marginTop: "10px", padding: "10px 20px" }}
        onClick={handleSubmit}
      >
        Analyze Ticket
      </button>
    </div>
  );
}