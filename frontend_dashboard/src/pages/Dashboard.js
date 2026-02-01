import React, { useEffect, useState } from "react";
import { fetchDetectedObjects, fetchAlerts } from "../api/detectedObjects";

export default function Dashboard() {
  const [objects, setObjects] = useState([]);
  const [alerts, setAlerts] = useState([]);

  const loadData = async () => {
    try {
      const [objRes, alertRes] = await Promise.all([
        fetchDetectedObjects(),
        fetchAlerts(),
      ]);
      setObjects(objRes.data);
      setAlerts(alertRes.data);
    } catch (err) {
      console.error("Dashboard load failed", err);
    }
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: 20 }}>
      <h2>Detected Objects</h2>
      <table border="1" cellPadding="8">
        <thead>
          <tr>
            <th>Type</th>
            <th>Confidence</th>
            <th>Status</th>
            <th>Camera</th>
          </tr>
        </thead>
        <tbody>
          {objects.map((o) => (
            <tr key={o.id}>
              <td>{o.object_type}</td>
              <td>{(o.confidence * 100).toFixed(2)}%</td>
              <td>{o.status}</td>
              <td>{o.camera_source_id}</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 style={{ marginTop: 30 }}>Alerts</h2>
      <ul>
        {alerts.map((a) => (
          <li key={a.id}>
            <strong>{a.severity.toUpperCase()}</strong> — {a.message}
          </li>
        ))}
      </ul>
    </div>
  );
}

