export default function ClassificationCard({ majorCategory, subCategory }) {

  if (!majorCategory) return null;

  return (
    <div style={{ marginTop: "20px" }}>
      <h3>Issue Category</h3>
      <p>{majorCategory} → {subCategory}</p>
    </div>
  );
}