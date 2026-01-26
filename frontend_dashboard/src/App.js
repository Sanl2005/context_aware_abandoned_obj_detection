import React, { useEffect, useState } from "react";
import axios from "axios";

const API = "http://127.0.0.1:3000/api";

function App() {
  const [objects, setObjects] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [risks, setRisks] = useState([]);

  const fetchData = async () => {
    try {
      const objRes = await axios.get(`${API}/detected_objects`);
      const alertRes = await axios.get(`${API}/alerts`);
      const riskRes = await axios.get(`${API}/risk_assessments`);

      setObjects(objRes.data);
      setAlerts(alertRes.data);
      setRisks(riskRes.data);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>🚨 Abandoned Object Detection Dashboard</h1>

      <h2>📌 Detected Objects</h2>
      <ul>
        {objects.map((obj) => (
          <li key={obj.id}>
            <b>{obj.object_type}</b> | Confidence: {obj.confidence} | Status:{" "}
            {obj.status} | Camera ID: {obj.camera_source_id}
          </li>
        ))}
      </ul>

      <h2>⚠ Alerts</h2>
      <ul>
        {alerts.map((a) => (
          <li key={a.id}>
            <b>{a.severity.toUpperCase()}</b> - {a.message} (Object ID:{" "}
            {a.detected_object_id})
          </li>
        ))}
      </ul>

      <h2>📊 Risk Assessments</h2>
      <ul>
        {risks.map((r) => (
          <li key={r.id}>
            Risk: <b>{r.risk_level}</b> | Score: {r.risk_score} | Reason:{" "}
            {r.reason}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;
