export default function DetectedObjectsTable({ data }) {
  return (
    <>
      <h3>📦 Detected Objects</h3>
      <table border="1" width="100%" cellPadding="8">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Confidence</th>
            <th>Status</th>
            <th>Camera</th>
          </tr>
        </thead>
        <tbody>
          {data.map(obj => (
            <tr key={obj.id}>
              <td>{obj.id}</td>
              <td>{obj.object_type}</td>
              <td>{obj.confidence.toFixed(2)}</td>
              <td>{obj.status}</td>
              <td>{obj.camera_source_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
