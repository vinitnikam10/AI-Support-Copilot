export default function ClassificationCard({ category }) {

  if (!category) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Issue Category</h3>
      <p>{category}</p>
    </div>
  );
}