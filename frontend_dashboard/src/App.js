import React, { useState, useEffect, useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import "./App.css";
import VideoFeed from "./components/VideoFeed";
import Login from "./pages/Login";
import { AuthContext } from "./auth/AuthContext";
import { ThemeContext } from "./context/ThemeContext";
import AbandonedObjectsList from "./components/AbandonedObjectsList";

// Protected Route Component
function ProtectedRoute({ children }) {
    const { user } = useContext(AuthContext);

    if (!user) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

// Polling Component for Real-time Stats
function LogicStatusCard() {
    const [stats, setStats] = useState(null);

    useEffect(() => {
        const fetchStats = () => {
            fetch("http://127.0.0.1:5000/stats")
                .then(res => res.json())
                .then(data => setStats(data))
                .catch(err => console.error("Stats poll failed", err));
        };

        fetchStats();
        const interval = setInterval(fetchStats, 1000); // Poll every second
        return () => clearInterval(interval);
    }, []);

    if (!stats || stats.status === "initializing") {
        return <div>Loading real-time logic status...</div>;
    }

    return (
        <div className="animate-slide-up">
            <div className="logic-grid">
                <div className="logic-item delay-100" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        <span className="status-dot green"></span>
                        <strong style={{ color: 'var(--accent-blue)' }}>Location Context</strong>
                    </div>
                    <select
                        className="fancy-button"
                        value={stats.location_type}
                        onChange={(e) => {
                            const newLocation = e.target.value;
                            // Optimistic update
                            setStats(prev => ({ ...prev, location_type: newLocation }));

                            fetch("http://127.0.0.1:5000/set_location", {
                                method: "POST",
                                headers: { "Content-Type": "application/json" },
                                body: JSON.stringify({ location_type: newLocation })
                            })
                                .then(res => res.json())
                                .then(data => {
                                    if (data.status !== 'success') {
                                        alert("Failed to update location: " + data.message);
                                    }
                                })
                                .catch(err => console.error("Error updating location:", err));
                        }}
                        style={{
                            width: '100%', padding: '8px', borderRadius: '8px',
                            border: '1px solid rgba(59, 130, 246, 0.4)',
                            background: 'rgba(59, 130, 246, 0.1)',
                            color: 'var(--text-primary)',
                            fontSize: '0.9em', fontWeight: 'bold', cursor: 'pointer'
                        }}
                    >
                        <option value="PUBLIC_OPEN_CROWDED">Public Open (Crowded)</option>
                        <option value="PUBLIC_REMOTE_AREA">Public Remote Area</option>
                        <option value="SEMI_RESTRICTED_ZONE">Semi-Restricted Zone</option>
                    </select>
                </div>

                <div className="logic-item delay-200" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        <span className="status-dot green"></span>
                        <strong style={{ color: 'var(--accent-blue)' }}>Density</strong>
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '800' }}>
                        {stats.crowd_density} <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>ppl</span>
                    </div>
                </div>

                <div className="logic-item delay-300" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        <span className="status-dot green"></span>
                        <strong style={{ color: 'var(--accent-blue)' }}>Active Intel</strong>
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '800' }}>
                        {stats.active_objects} <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>obj</span>
                    </div>
                </div>

                <div className="logic-item delay-400" style={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
                        <span className={`status-dot ${stats.high_risk_count > 0 ? 'red' : 'green'}`}></span>
                        <strong style={{ color: stats.high_risk_count > 0 ? 'var(--accent-red)' : 'var(--accent-blue)' }}>High Risk</strong>
                    </div>
                    <div style={{ fontSize: '1.5rem', fontWeight: '800', color: stats.high_risk_count > 0 ? 'var(--accent-red)' : 'var(--text-primary)' }}>
                        {stats.high_risk_count} <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>alerts</span>
                    </div>
                </div>

                {stats.modules && Object.entries(stats.modules)
                    .filter(([key]) => key !== 'Occlusion_Aware' && key !== 'Behavior_Intelligent')
                    .map(([key, isActive], i) => (
                        <div className={`logic-item delay-${((i % 5) + 5) * 100}`} key={key}>
                            <span className={`status-dot ${isActive ? 'green' : 'gray'}`}></span>
                            <strong style={{ flex: 1 }}>{key.replace(/_/g, ' ')}</strong>
                            <span style={{
                                padding: '2px 8px', borderRadius: '12px', fontSize: '0.75rem', fontWeight: 'bold',
                                background: isActive ? 'rgba(16, 185, 129, 0.2)' : 'rgba(100, 116, 139, 0.2)',
                                color: isActive ? 'var(--accent-green)' : 'var(--text-secondary)'
                            }}>
                                {isActive ? 'ON' : 'OFF'}
                            </span>
                        </div>
                    ))}
            </div>
            <p className="animate-slide-up delay-500" style={{ marginTop: '20px', fontSize: '0.9em', color: 'var(--accent-blue)', background: 'rgba(59, 130, 246, 0.1)', padding: '12px', borderRadius: '8px', borderLeft: '4px solid var(--accent-blue)' }}>
                <span style={{ marginRight: '10px' }}>⚡</span>
                System is performing <strong>Real-time Contextual Analysis</strong>. Adaptivity is <strong>Online</strong>.
            </p>
        </div>
    );
}

// Main Dashboard Component
function Dashboard() {
    const [mlServiceStatus, setMlServiceStatus] = useState("checking...");
    const { user, logout } = useContext(AuthContext);
    const { theme, toggleTheme } = useContext(ThemeContext);

    // State for objects needed for both Main List and Alerts
    const [objects, setObjects] = useState([]);
    const [loadingObjects, setLoadingObjects] = useState(true);

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

        // Fetch Objects Loop
        const fetchObjects = () => {
            fetch("http://127.0.0.1:5000/objects")
                .then((res) => res.json())
                .then((data) => {
                    if (data.status === "success") {
                        setObjects(data.objects);
                    }
                    setLoadingObjects(false);
                })
                .catch((err) => {
                    console.error("Error fetching objects:", err);
                    setLoadingObjects(false);
                });
        };

        // Fetch immediately
        fetchObjects();

        // Then fetch every 2 seconds for real-time updates
        const interval = setInterval(fetchObjects, 2000);

        return () => clearInterval(interval);
    }, []);

    // Derived alerts
    const alerts = objects.filter(obj => obj.threat_level === 'HIGH_RISK' || obj.confidence > 0.8);

    return (
        <div className="dashboard-container">
            <header className="dashboard-header">
                <div className="logo-section">
                    <div className="logo-glow"></div>
                    <div className="logo-container">
                        <svg className="logo-icon" width="40" height="40" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z" fill="url(#logo-gradient)" />
                            <defs>
                                <linearGradient id="logo-gradient" x1="1" y1="4.5" x2="23" y2="19.5" gradientUnits="userSpaceOnUse">
                                    <stop stopColor="#60a5fa" />
                                    <stop offset="1" stopColor="#a78bfa" />
                                </linearGradient>
                            </defs>
                        </svg>
                    </div>
                    <div className="title-wrapper">
                        <h1 className="app-title">Smart Look</h1>
                        <span className="app-subtitle">AI Surveillance Dashboard</span>
                    </div>
                </div>

                <div className="header-controls animate-slide-right">
                    <div className="user-profile-pill">
                        <div className="user-avatar">
                            {user?.username ? user.username.charAt(0).toUpperCase() : 'U'}
                        </div>
                        <span className="user-name">{user?.username}</span>
                    </div>

                    <button className="control-btn logout-btn fancy-button" onClick={logout} title="Logout">
                        Logout
                    </button>
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
                {/* Left Column: Video & Alerts */}
                <div className="list-container">
                    <section className="video-section">
                        <VideoFeed />
                    </section>

                    {/* Alerts Section */}
                    <section className="alerts-section animate-slide-up delay-200">
                        <h2 className="section-header" style={{ color: '#ef4444' }}>
                            <span role="img" aria-label="warning">
                                ⚠️
                            </span>{" "}
                            System Alerts
                        </h2>
                        <div className="card">
                            <AlertsDisplay alerts={alerts} />
                        </div>
                    </section>
                </div>

                {/* Right Column: Logic Status & Detected Objects */}
                <div className="list-container">
                    {/* Detected Objects Section - Moved to Top */}
                    <div className="animate-slide-up delay-100">
                        <h2 className="section-header">
                            <span role="img" aria-label="package">
                                📦
                            </span>{" "}
                            Detected Objects
                        </h2>
                        <div className="card">
                            <LiveObjectsDisplay objects={objects} loading={loadingObjects} />
                        </div>
                    </div>

                    {/* System Logic Status Major Section - Moved Below */}
                    <section className="logic-status-section animate-slide-up delay-300">
                        <h2 className="section-header">
                            <span role="img" aria-label="brain">
                                🧠
                            </span>{" "}
                            Active Intelligence Modules
                        </h2>
                        <div className="card">
                            <LogicStatusCard />
                        </div>
                    </section>
                </div>
            </div>

            {/* Abandoned Objects Historical Feed */}
            <hr style={{ margin: '40px 0', borderColor: 'var(--border-color)', opacity: 0.2 }} />
            <AbandonedObjectsList />
        </div>
    );
}

// Alerts Display Component
function AlertsDisplay({ alerts }) {
    if (alerts.length === 0) {
        return (
            <div style={{ padding: '20px', textAlign: 'center', color: '#94a3b8' }}>
                <span style={{ fontSize: '24px', display: 'block', marginBottom: '10px' }}>✅</span>
                No active security alerts
            </div>
        );
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {alerts.map((obj, i) => (
                <div key={`alert-${obj.object_id}`} className={`alert-item delay-${(i % 5 + 1) * 100}`}>
                    <div className="alert-title">
                        <span>{obj.threat_level.replace('_', ' ')} DETECTED</span>
                        <span style={{ fontSize: '0.8em' }}>{new Date().toLocaleTimeString()}</span>
                    </div>
                    <div className="alert-msg">
                        <strong>{obj.class_name}</strong> (ID: {obj.object_id}) is in <strong>{obj.state}</strong> state.
                        Confidence: {(obj.confidence * 100).toFixed(0)}%.
                        {obj.owner_id ? ` Owner: ${obj.owner_id}` : ' No owner detected.'}
                    </div>
                </div>
            ))}
        </div>
    );
}

// Live Objects Display Component
function LiveObjectsDisplay({ objects, loading }) {
    // Format idle time
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

    // Get threat badge color
    const getThreatColor = (level) => {
        if (level === 'HIGH_RISK') return '#ef4444';
        if (level === 'MEDIUM_RISK') return '#f59e0b';
        return '#10b981';
    };

    if (loading) {
        return <p style={{ textAlign: 'center', padding: '20px' }}>Loading objects...</p>;
    }

    if (objects.length === 0) {
        return (
            <div style={{ textAlign: 'center', padding: '30px', color: '#94a3b8' }}>
                <p style={{ fontSize: '48px', margin: '0' }}>🔍</p>
                <p style={{ margin: '10px 0 0 0' }}>No objects detected</p>
            </div>
        );
    }

    return (
        <div className="animate-slide-up" style={{ maxHeight: '400px', overflowY: 'auto', paddingRight: '10px' }}>
            {objects.map((obj, i) => (
                <div
                    key={obj.object_id}
                    className={`live-object-item delay-${(i % 5 + 1) * 100}`}
                    style={{
                        padding: '15px',
                        marginBottom: '10px',
                        background: 'rgba(59, 130, 246, 0.05)',
                        borderRadius: '8px',
                        border: '1px solid rgba(59, 130, 246, 0.2)'
                    }}
                >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                        <strong style={{ fontSize: '16px' }}>{obj.class_name}</strong>
                        <span
                            style={{
                                padding: '4px 8px',
                                borderRadius: '4px',
                                fontSize: '12px',
                                background: getThreatColor(obj.threat_level),
                                color: 'white',
                                fontWeight: 'bold'
                            }}
                        >
                            {obj.threat_level.replace('_', ' ')}
                        </span>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px', fontSize: '14px' }}>
                        <div>
                            <span style={{ color: '#94a3b8' }}>ID:</span> {obj.object_id}
                        </div>
                        <div>
                            <span style={{ color: '#94a3b8' }}>State:</span> {obj.state}
                        </div>
                        {obj.class_name !== 'person' && (
                            <>
                                <div>
                                    <span style={{ color: '#94a3b8' }}>Confidence:</span> {(obj.confidence * 100).toFixed(0)}%
                                </div>
                                <div>
                                    <span style={{ color: '#94a3b8' }}>Idle Time:</span>{' '}
                                    <strong style={{ color: getIdleTimeColor(obj.idle_time) }}>
                                        {formatIdleTime(obj.idle_time)}
                                    </strong>
                                </div>
                                <div style={{ gridColumn: '1 / -1' }}>
                                    <span style={{ color: '#94a3b8' }}>Owner:</span>{' '}
                                    {obj.owner_id ? (
                                        <span>
                                            <strong>{obj.owner_id}</strong>
                                            {obj.owner_absence_time > 0 && (
                                                <span style={{ marginLeft: '10px', color: '#f59e0b', fontWeight: 'bold' }}>
                                                    ⏱️ Absent: {formatIdleTime(obj.owner_absence_time)}
                                                </span>
                                            )}
                                            {obj.owner_distance !== null && (
                                                <span style={{
                                                    color: obj.owner_distance < 2 ? '#10b981' : obj.owner_distance < 5 ? '#f59e0b' : '#ef4444',
                                                    marginLeft: '8px'
                                                }}>
                                                    ({obj.owner_distance}m away)
                                                </span>
                                            )}
                                        </span>
                                    ) : (
                                        <span style={{ color: '#ef4444', fontWeight: 'bold' }}>⚠️ No owner</span>
                                    )}
                                </div>
                            </>
                        )}
                    </div>
                </div>
            ))
            }
        </div >
    );
}

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/login" element={<Login />} />
                <Route
                    path="/"
                    element={
                        <ProtectedRoute>
                            <Dashboard />
                        </ProtectedRoute>
                    }
                />
                <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
