export default function SimilarTickets({ tickets }) {

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Similar Past Issues</h3>

      {(!tickets || tickets.length === 0) ? (
        <p style={{ opacity: 0.7 }}>
          No similar tickets found in the knowledge base.
        </p>
      ) : (
        <ul>
          {tickets.map((ticket, index) => (
            <li key={index}>{ticket}</li>
          ))}
        </ul>
      )}

    </div>
  );
}