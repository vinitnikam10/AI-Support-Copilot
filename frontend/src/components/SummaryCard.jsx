export default function SummaryCard({ summary }) {

  if (!summary) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Summary</h3>
      <p>{summary}</p>
    </div>
  );
}