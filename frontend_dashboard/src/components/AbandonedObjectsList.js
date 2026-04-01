import React, { useState, useEffect } from 'react';

const AbandonedObjectsList = () => {
    const [objects, setObjects] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [expandedPersons, setExpandedPersons] = useState({});

    const togglePerson = (id) => {
        setExpandedPersons(prev => ({ ...prev, [id]: !prev[id] }));
    };

    const API_BASE = 'http://localhost:3000/api';

    // 6. Example React fetch usage
    const fetchObjects = async () => {
        try {
            const response = await fetch(`${API_BASE}/abandoned_objects`, {
                headers: {
                    // Include any authorization token if necessary
                    // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Failed to fetch abandoned objects');
            const data = await response.json();
            setObjects(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchObjects();
        // Dynamic fast polling for real-time list updates
        const interval = setInterval(fetchObjects, 2000);
        return () => clearInterval(interval);
    }, []);

    // 7. Example "Mark as Permanent" button handler
    const makePermanent = async (id) => {
        try {
            const response = await fetch(`${API_BASE}/abandoned_objects/${id}/make_permanent`, {
                method: 'PATCH',
                headers: {
                    // 'Authorization': `Bearer ${localStorage.getItem('token')}`,
                    'Content-Type': 'application/json'
                }
            });
            if (!response.ok) throw new Error('Failed to update object status');
            const updatedObject = await response.json();

            // Update local state without full refresh
            setObjects(objects.map(obj => obj.id === id ? updatedObject : obj));
        } catch (err) {
            console.error(err);
            alert('Failed to mark as permanent');
        }
    };

    const deleteObject = async (id) => {
        if (!window.confirm("Are you sure you want to manually delete this record?")) return;
        try {
            const response = await fetch(`${API_BASE}/abandoned_objects/${id}`, {
                method: 'DELETE',
                // headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
            });
            if (!response.ok) throw new Error('Failed to delete object');
            setObjects(objects.filter(obj => obj.id !== id));
        } catch (err) {
            console.error(err);
            alert('Failed to delete object');
        }
    };

    if (loading) return <div style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00e5ff', padding: '20px', letterSpacing: '0.1em' }}>// LOADING RECORDS...</div>;
    if (error) return <div style={{ fontFamily: 'Share Tech Mono, monospace', color: '#ff1744', padding: '20px' }}>// ERROR: {error}</div>;

    return (
        <div className="abandoned-objects-container animate-slide-up" style={{ padding: '20px' }}>
            <h2 className="section-header" style={{ marginBottom: '20px' }}>
                📷 ARCHIVED ABANDONED OBJECTS
            </h2>
            {objects.length === 0 ? (
                <div className="empty-state">
                    <span style={{ fontSize: '3rem', display: 'block', marginBottom: '10px' }}>📭</span>
                    <p>No recent abandoned objects found.</p>
                </div>
            ) : (
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
                    {objects.map((obj, i) => (
                        <div key={obj.id} className={`card delay-${(i % 5 + 1) * 100}`} style={{ padding: '0', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
                            <div style={{ display: 'flex', height: '140px', background: 'rgba(0, 10, 14, 0.8)', borderBottom: '1px solid rgba(0,229,255,0.12)' }}>
                                {obj.object_image_url ? (
                                    <div style={{ flex: 1, position: 'relative' }}>
                                        <div style={{ position: 'absolute', top: '6px', left: '6px', background: 'rgba(0,10,14,0.85)', padding: '2px 8px', border: '1px solid rgba(0,229,255,0.35)', fontSize: '0.65rem', color: '#00e5ff', fontFamily: 'Share Tech Mono, monospace', letterSpacing: '0.1em', textTransform: 'uppercase' }}>
                                            {obj.object_type || 'OBJECT'}
                                        </div>
                                        <img src={obj.object_image_url.startsWith('http') ? obj.object_image_url : `http://localhost:3000${obj.object_image_url}`} alt="Object" style={{ width: '100%', height: '100%', objectFit: 'cover', filter: 'brightness(0.9) saturate(0.8)' }} />
                                    </div>
                                ) : (
                                    <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,10,14,0.6)', color: '#2d6e7a', fontFamily: 'Share Tech Mono, monospace', fontSize: '0.75rem', letterSpacing: '0.1em' }}>// NO IMAGE</div>
                                )}
                            </div>

                            <div style={{ padding: '16px', display: 'flex', flexDirection: 'column', flex: 1, gap: '10px' }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <div style={{ fontSize: '0.62rem', color: '#2d6e7a', textTransform: 'uppercase', letterSpacing: '0.15em', marginBottom: '3px', fontFamily: 'Share Tech Mono, monospace' }}>// TRACKING ID</div>
                                        <div style={{ fontFamily: 'Share Tech Mono, monospace', color: '#00e5ff', fontSize: '0.85rem', textShadow: '0 0 8px rgba(0,229,255,0.4)' }}>{obj.tracking_id.split('-')[0]}...</div>
                                    </div>
                                    <span className={`badge ${obj.threat_level === 'HIGH_RISK' ? 'abandoned' : 'detected'}`}>
                                        {obj.threat_level.replace('_', ' ')}
                                    </span>
                                </div>

                                <div style={{ display: 'flex', gap: '6px', flexDirection: 'column', fontFamily: 'Share Tech Mono, monospace', fontSize: '0.78rem' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(0,229,255,0.06)' }}>
                                        <span style={{ color: '#2d6e7a' }}>OWNER_ID</span>
                                        <span style={{ color: '#cffafe' }}>{obj.person_id || '—'}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(0,229,255,0.06)' }}>
                                        <span style={{ color: '#2d6e7a' }}>CONFIDENCE</span>
                                        <span style={{ color: obj.abandonment_score > 0.8 ? '#ff1744' : '#00e5ff' }}>{(obj.abandonment_score * 100).toFixed(0)}%</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0', borderBottom: '1px solid rgba(0,229,255,0.06)' }}>
                                        <span style={{ color: '#2d6e7a' }}>TIMESTAMP</span>
                                        <span style={{ color: '#cffafe' }}>{new Date(obj.detected_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                                    </div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between', padding: '4px 0' }}>
                                        <span style={{ color: '#2d6e7a' }}>STATUS</span>
                                        {obj.is_permanent ? (
                                            <span style={{ color: '#00e676', textShadow: '0 0 8px rgba(0,230,118,0.4)' }}>STORED_FOREVER</span>
                                        ) : (
                                            <span style={{ color: '#7c4dff' }}>
                                                EXP {new Date(obj.expires_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </span>
                                        )}
                                    </div>
                                </div>

                                {obj.person_image_url && (
                                    <div style={{ marginTop: '8px' }}>
                                        <button
                                            onClick={() => togglePerson(obj.id)}
                                            style={{ background: 'rgba(0,229,255,0.05)', border: '1px solid rgba(0,229,255,0.25)', color: '#00e5ff', cursor: 'pointer', fontSize: '0.7rem', fontFamily: 'Share Tech Mono, monospace', padding: '5px 12px', letterSpacing: '0.1em', display: 'flex', alignItems: 'center', gap: '6px', borderRadius: '2px', transition: 'all 0.2s ease' }}
                                            onMouseOver={e => { e.currentTarget.style.background = 'rgba(0,229,255,0.12)'; e.currentTarget.style.boxShadow = '0 0 10px rgba(0,229,255,0.15)'; }}
                                            onMouseOut={e => { e.currentTarget.style.background = 'rgba(0,229,255,0.05)'; e.currentTarget.style.boxShadow = 'none'; }}
                                        >
                                            {expandedPersons[obj.id] ? '▲ HIDE SUBJECT' : '▶ VIEW SUBJECT'}
                                        </button>

                                        {expandedPersons[obj.id] && (
                                            <div style={{ marginTop: '8px', overflow: 'hidden', border: '1px solid rgba(0,229,255,0.2)', background: 'rgba(0,10,14,0.8)' }}>
                                                <div style={{ padding: '4px 10px', background: 'rgba(0,229,255,0.08)', fontSize: '0.62rem', color: '#5eead4', fontFamily: 'Share Tech Mono, monospace', letterSpacing: '0.15em', borderBottom: '1px solid rgba(0,229,255,0.1)' }}>// LAST INTERACTED SUBJECT</div>
                                                <img src={obj.person_image_url.startsWith('http') ? obj.person_image_url : `http://localhost:3000${obj.person_image_url}`} alt="Person" style={{ width: '100%', maxHeight: '180px', objectFit: 'contain', display: 'block', filter: 'contrast(1.1) saturate(0.8)' }} />
                                            </div>
                                        )}
                                    </div>
                                )}


                                <div style={{ marginTop: 'auto', paddingTop: '12px', borderTop: '1px solid rgba(0,229,255,0.1)', display: 'flex', gap: '8px' }}>
                                    {!obj.is_permanent && (
                                        <button
                                            className="fancy-button"
                                            onClick={() => makePermanent(obj.id)}
                                            style={{ flex: 1, background: 'rgba(0, 230, 118, 0.06)', color: '#00e676', border: '1px solid rgba(0,230,118,0.25)', padding: '8px', borderRadius: '2px', cursor: 'pointer', fontFamily: 'Share Tech Mono, monospace', fontSize: '0.7rem', letterSpacing: '0.08em', transition: 'all 0.2s' }}
                                            onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(0, 230, 118, 0.14)'; e.currentTarget.style.boxShadow = '0 0 10px rgba(0,230,118,0.15)'; }}
                                            onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(0, 230, 118, 0.06)'; e.currentTarget.style.boxShadow = 'none'; }}
                                        >
                                            KEEP_PERMANENT
                                        </button>
                                    )}
                                    <button
                                        className="fancy-button"
                                        onClick={() => deleteObject(obj.id)}
                                        style={{ flex: obj.is_permanent ? 1 : 0.5, background: 'rgba(255, 23, 68, 0.06)', color: '#ff1744', border: '1px solid rgba(255,23,68,0.25)', padding: '8px', borderRadius: '2px', cursor: 'pointer', fontFamily: 'Share Tech Mono, monospace', fontSize: '0.7rem', letterSpacing: '0.08em', transition: 'all 0.2s' }}
                                        onMouseOver={(e) => { e.currentTarget.style.background = 'rgba(255, 23, 68, 0.14)'; e.currentTarget.style.boxShadow = '0 0 10px rgba(255,23,68,0.2)'; }}
                                        onMouseOut={(e) => { e.currentTarget.style.background = 'rgba(255, 23, 68, 0.06)'; e.currentTarget.style.boxShadow = 'none'; }}
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AbandonedObjectsList;
