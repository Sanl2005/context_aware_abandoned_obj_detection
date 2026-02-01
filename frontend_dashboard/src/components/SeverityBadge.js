export default function SeverityBadge({ level }) {
  const colors = {
    high: "#e74c3c",
    medium: "#f39c12",
    low: "#2ecc71"
  };

  return (
    <span style={{
      background: colors[level],
      color: "#fff",
      padding: "4px 8px",
      borderRadius: "4px",
      fontSize: "12px"
    }}>
      {level.toUpperCase()}
    </span>
  );
}
