import React, { useState, useEffect } from "react";
import "./App.css";
import VideoFeed from "./components/VideoFeed";

function App() {
    const [mlServiceStatus, setMlServiceStatus] = useState("checking...");

    useEffect(() => {
        // Check if ML service is running
        fetch("http://127.0.0.1:5000/status")
            .then((res) => res.json())
            .then((data) => {
                setMlServiceStatus(`✅ ${data.message}`);
            })
            .catch((err) => {
                setMlServiceStatus("❌ ML Service not running");
            });
    }, []);

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="dashboard-title">
                    <span role="img" aria-label="siren">
                        🚨
                    </span>{" "}
                    SentinelEye Dashboard
                </div>
                <div className="live-indicator">
                    <div className="pulse"></div> Live Monitor
                </div>
            </header>

            {/* ML Service Status */}
            <div style={{
                padding: '10px 20px',
                background: 'rgba(59, 130, 246, 0.1)',
                borderRadius: '8px',
                marginBottom: '20px',
                border: '1px solid rgba(59, 130, 246, 0.3)'
            }}>
                <strong>ML Service Status:</strong> {mlServiceStatus}
            </div>

            <div className="dashboard-grid">
                {/* Live Video Feed Section */}
                <section className="video-section">
                    <VideoFeed />
                </section>

                {/* Simplified info section */}
                <section>
                    <h2 className="section-header">
                        <span role="img" aria-label="info">
                            ℹ️
                        </span>{" "}
                        System Info
                    </h2>
                    <div className="card">
                        <h3>Video Feed Active</h3>
                        <p>
                            The live video feed is showing real-time object detection from
                            your webcam.
                        </p>
                        <ul>
                            <li>🟢 Green boxes: High confidence (&gt;70%)</li>
                            <li>🟠 Orange boxes: Medium confidence</li>
                            <li>🔴 Red boxes: Abandoned objects (&gt;5s stationary)</li>
                        </ul>
                    </div>
                </section>

                <aside className="list-container">
                    <div>
                        <h2 className="section-header">
                            <span role="img" aria-label="gear">
                                ⚙️
                            </span>{" "}
                            Services
                        </h2>
                        <div className="card">
                            <p>
                                <strong>ML Service (Flask):</strong>
                                <br />
                                Port 5000 - Video streaming
                            </p>
                            <p style={{ marginTop: "10px", fontSize: "12px", color: "#94a3b8" }}>
                                Note: Rails backend is optional for video feed functionality.
                                Start Rails on port 3000 to enable detection history and alerts.
                            </p>
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    );
}

export default App;
