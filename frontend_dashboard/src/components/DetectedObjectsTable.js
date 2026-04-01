import React from 'react';

export default function DetectedObjectsTable({ data }) {
  // Format idle time to show minutes and seconds
  const formatIdleTime = (seconds) => {
    if (!seconds || seconds < 1) return '< 1s';
    if (seconds < 60) return `${Math.floor(seconds)}s`;
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}m ${secs}s`;
  };

  // Get color based on idle time
  const getIdleTimeColor = (seconds) => {
    if (seconds < 10) return '#10b981'; // green
    if (seconds < 30) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };

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
            <th>Idle Time</th>
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
              <td style={{
                color: getIdleTimeColor(obj.idle_time || 0),
                fontWeight: 'bold'
              }}>
                {formatIdleTime(obj.idle_time || 0)}
              </td>
              <td>{obj.camera_source_id}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </>
  );
}
