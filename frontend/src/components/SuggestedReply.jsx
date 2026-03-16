export default function SuggestedReply({ reply }) {

  if (!reply) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Suggested Reply</h3>

      <textarea
        rows="6"
        style={{ width: "100%", padding: "10px" }}
        value={reply}
        readOnly
      />
    </div>
  );
}