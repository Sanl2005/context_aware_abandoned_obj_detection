import React, { useState, useRef, useEffect, useCallback } from 'react';

const API = 'http://127.0.0.1:5000';

// ─── Format helpers ──────────────────────────────────────────────────────────
const fmtElapsed = (secs) => {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = Math.floor(secs % 60);
    if (h > 0) return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
};

const fmtDate = (iso) => {
    const d = new Date(iso);
    return d.toLocaleString(undefined, { dateStyle: 'medium', timeStyle: 'short' });
};

// ─── Recording Library Modal ─────────────────────────────────────────────────
function RecordingsLibrary({ onClose }) {
    const [recordings, setRecordings] = useState([]);
    const [loading, setLoading] = useState(true);
    const [playingFile, setPlayingFile] = useState(null);

    // PTZ state
    const [zoom, setZoom] = useState(1);
    const [pan, setPan] = useState({ x: 0, y: 0 });
    const isDragging = useRef(false);
    const lastPos = useRef({ x: 0, y: 0 });

    const handleMouseDown = (e) => {
        if (zoom > 1) {
            isDragging.current = true;
            lastPos.current = { x: e.clientX, y: e.clientY };
        }
    };

    const handleMouseMove = (e) => {
        if (isDragging.current) {
            const dx = e.clientX - lastPos.current.x;
            const dy = e.clientY - lastPos.current.y;
            lastPos.current = { x: e.clientX, y: e.clientY };
            setPan(p => ({ x: p.x + dx, y: p.y + dy }));
        }
    };

    const handleMouseUp = () => {
        isDragging.current = false;
    };

    const fetchRecordings = useCallback(() => {
        setLoading(true);
        fetch(`${API}/recordings`)
            .then(r => r.json())
            .then(d => {
                if (d.status === 'success') setRecordings(d.recordings);
            })
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const deleteRecording = useCallback((filename) => {
        if (!window.confirm(`Are you sure you want to delete ${filename}?`)) return;
        fetch(`${API}/recordings/${filename}`, { method: 'DELETE' })
            .then(r => r.json())
            .then(d => {
                if (d.status === 'success') {
                    if (playingFile === filename) setPlayingFile(null);
                    fetchRecordings();
                } else {
                    alert('Error deleting: ' + d.message);
                }
            })
            .catch(console.error);
    }, [fetchRecordings, playingFile]);

    useEffect(() => {
        fetchRecordings();
    }, [fetchRecordings]);

    return (
        <div style={{
            position: 'fixed', inset: 0,
            background: 'rgba(2, 12, 14, 0.92)',
            backdropFilter: 'blur(12px)',
            zIndex: 1000,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            animation: 'slideUpFade 0.3s ease'
        }}>
            <div style={{
                background: 'rgba(0, 20, 28, 0.97)',
                border: '1px solid rgba(0, 229, 255, 0.35)',
                borderRadius: '8px',
                width: '90%', maxWidth: '900px',
                maxHeight: '90vh',
                display: 'flex', flexDirection: 'column',
                boxShadow: '0 0 60px rgba(0,229,255,0.15), 0 24px 48px rgba(0,0,0,0.7)',
                overflow: 'hidden'
            }}>
                {/* Header */}
                <div style={{
                    padding: '1.25rem 1.5rem',
                    borderBottom: '1px solid rgba(0, 229, 255, 0.2)',
                    background: 'rgba(0, 15, 20, 0.8)',
                    display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                    flexShrink: 0
                }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                        <span style={{ fontSize: '1.3rem' }}>🎬</span>
                        <div>
                            <div style={{
                                fontFamily: 'var(--font-display)', fontSize: '0.9rem',
                                color: 'var(--cyan-primary)', letterSpacing: '0.2em',
                                textTransform: 'uppercase', textShadow: '0 0 12px rgba(0,229,255,0.5)'
                            }}>
                                Recordings Library
                            </div>
                            <div style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                                {recordings.length} recording{recordings.length !== 1 ? 's' : ''} stored
                            </div>
                        </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                        <button
                            onClick={fetchRecordings}
                            style={{
                                padding: '6px 14px', borderRadius: '6px',
                                background: 'rgba(0, 229, 255, 0.08)',
                                border: '1px solid rgba(0, 229, 255, 0.3)',
                                color: 'var(--cyan-primary)', cursor: 'pointer',
                                fontSize: '0.8rem', fontFamily: 'var(--font-mono)'
                            }}
                        >
                            ↻ Refresh
                        </button>
                        <button
                            onClick={onClose}
                            style={{
                                padding: '6px 14px', borderRadius: '6px',
                                background: 'rgba(255, 23, 68, 0.08)',
                                border: '1px solid rgba(255, 23, 68, 0.3)',
                                color: 'var(--red-alert)', cursor: 'pointer',
                                fontSize: '0.85rem', fontFamily: 'var(--font-mono)'
                            }}
                        >
                            ✕ Close
                        </button>
                    </div>
                </div>

                {/* Body */}
                <div style={{ overflowY: 'auto', flex: 1, padding: '1.25rem' }}>
                    {/* Inline video player */}
                    {playingFile && (
                        <div style={{
                            marginBottom: '1.25rem',
                            background: '#000',
                            borderRadius: '8px',
                            border: '1px solid rgba(0,229,255,0.3)',
                            overflow: 'hidden',
                            position: 'relative'
                        }}>
                            <div style={{
                                padding: '8px 14px',
                                background: 'rgba(0,15,20,0.9)',
                                borderBottom: '1px solid rgba(0,229,255,0.2)',
                                display: 'flex', alignItems: 'center', justifyContent: 'space-between'
                            }}>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.78rem', color: 'var(--cyan-primary)' }}>
                                    ▶ {playingFile}
                                </span>
                                <button
                                    onClick={() => setPlayingFile(null)}
                                    style={{
                                        background: 'none', border: 'none',
                                        color: 'var(--text-secondary)', cursor: 'pointer', fontSize: '1rem'
                                    }}
                                >✕</button>
                            </div>
                            <div
                                style={{
                                    width: '100%', maxHeight: '400px',
                                    overflow: 'hidden', position: 'relative',
                                    cursor: zoom > 1 ? (isDragging.current ? 'grabbing' : 'grab') : 'default'
                                }}
                                onMouseDown={handleMouseDown}
                                onMouseMove={handleMouseMove}
                                onMouseUp={handleMouseUp}
                                onMouseLeave={handleMouseUp}
                            >
                                <video
                                    key={playingFile}
                                    controls
                                    autoPlay
                                    style={{
                                        width: '100%', maxHeight: '400px', display: 'block', background: '#000',
                                        transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
                                        transformOrigin: 'center center',
                                        transition: isDragging.current ? 'none' : 'transform 0.2s ease-out'
                                    }}
                                    src={`${API}/recordings/${playingFile}`}
                                />
                            </div>

                            {/* PTZ Controls */}
                            <div style={{
                                padding: '8px 14px',
                                background: 'rgba(0,10,14,0.9)',
                                borderTop: '1px solid rgba(0,229,255,0.2)',
                                display: 'flex', gap: '8px', alignItems: 'center'
                            }}>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--text-secondary)', marginRight: '8px' }}>
                                    CCTV PTZ
                                </span>
                                <button
                                    onClick={() => setZoom(z => Math.min(z + 0.5, 4))}
                                    style={{
                                        padding: '4px 10px', background: 'rgba(0,229,255,0.1)', border: '1px solid rgba(0,229,255,0.3)',
                                        color: 'var(--cyan-primary)', borderRadius: '4px', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.8rem'
                                    }}
                                >🔍+</button>
                                <button
                                    onClick={() => setZoom(z => { const nz = Math.max(z - 0.5, 1); if (nz === 1) setPan({ x: 0, y: 0 }); return nz; })}
                                    style={{
                                        padding: '4px 10px', background: 'rgba(0,229,255,0.1)', border: '1px solid rgba(0,229,255,0.3)',
                                        color: 'var(--cyan-primary)', borderRadius: '4px', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.8rem'
                                    }}
                                >🔍-</button>
                                <button
                                    onClick={() => { setZoom(1); setPan({ x: 0, y: 0 }); }}
                                    style={{
                                        padding: '4px 10px', background: 'rgba(255,23,68,0.1)', border: '1px solid rgba(255,23,68,0.3)',
                                        color: 'var(--red-alert)', borderRadius: '4px', cursor: 'pointer', fontFamily: 'var(--font-mono)', fontSize: '0.8rem'
                                    }}
                                >Reset</button>
                                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.75rem', color: 'var(--cyan-dim)', marginLeft: '10px' }}>
                                    Zoom: {zoom}x {zoom > 1 ? '(Drag to pan)' : ''}
                                </span>
                            </div>
                        </div>
                    )}

                    {loading ? (
                        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                            <div style={{ fontSize: '2rem', marginBottom: '12px' }}>⏳</div>
                            Loading recordings...
                        </div>
                    ) : recordings.length === 0 ? (
                        <div style={{
                            textAlign: 'center', padding: '3rem',
                            color: 'var(--text-muted)', fontFamily: 'var(--font-mono)',
                            border: '1px dashed rgba(0,229,255,0.1)', borderRadius: '8px'
                        }}>
                            <div style={{ fontSize: '3rem', marginBottom: '12px' }}>📹</div>
                            <div>No recordings yet.</div>
                            <div style={{ fontSize: '0.8rem', marginTop: '8px', opacity: 0.7 }}>
                                Press the REC button on the video feed to start recording.
                            </div>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                            {recordings.map((rec, i) => (
                                <div
                                    key={rec.filename}
                                    style={{
                                        display: 'flex', alignItems: 'center', gap: '16px',
                                        padding: '14px 16px',
                                        background: playingFile === rec.filename
                                            ? 'rgba(0, 229, 255, 0.08)'
                                            : 'rgba(0, 20, 28, 0.7)',
                                        border: `1px solid ${playingFile === rec.filename ? 'rgba(0,229,255,0.4)' : 'rgba(0,229,255,0.15)'}`,
                                        borderRadius: '6px',
                                        transition: 'all 0.25s ease',
                                        animation: `slideUpFade 0.4s ease forwards`,
                                        animationDelay: `${i * 50}ms`,
                                        opacity: 0
                                    }}
                                >
                                    {/* Icon */}
                                    <div style={{
                                        width: '44px', height: '44px', flexShrink: 0,
                                        background: 'rgba(255, 23, 68, 0.1)',
                                        border: '1px solid rgba(255, 23, 68, 0.3)',
                                        borderRadius: '8px',
                                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                                        fontSize: '1.3rem'
                                    }}>
                                        🎥
                                    </div>

                                    {/* Info */}
                                    <div style={{ flex: 1, minWidth: 0 }}>
                                        <div style={{
                                            fontFamily: 'var(--font-mono)', fontSize: '0.81rem',
                                            color: 'var(--text-primary)',
                                            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis'
                                        }}>
                                            {rec.filename}
                                        </div>
                                        <div style={{ display: 'flex', gap: '16px', marginTop: '4px' }}>
                                            <span style={{ fontSize: '0.73rem', color: 'var(--text-secondary)', fontFamily: 'var(--font-mono)' }}>
                                                📅 {fmtDate(rec.recorded_at)}
                                            </span>
                                            <span style={{ fontSize: '0.73rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                                                💾 {rec.size_mb} MB
                                            </span>
                                        </div>
                                    </div>

                                    {/* Actions */}
                                    <div style={{ display: 'flex', gap: '8px', flexShrink: 0 }}>
                                        <button
                                            onClick={() => setPlayingFile(rec.filename === playingFile ? null : rec.filename)}
                                            title="Play"
                                            style={{
                                                padding: '6px 14px', borderRadius: '6px',
                                                background: playingFile === rec.filename
                                                    ? 'rgba(0,229,255,0.2)'
                                                    : 'rgba(0,229,255,0.08)',
                                                border: '1px solid rgba(0,229,255,0.3)',
                                                color: 'var(--cyan-primary)', cursor: 'pointer',
                                                fontSize: '0.8rem', fontFamily: 'var(--font-mono)',
                                                transition: 'all 0.2s ease'
                                            }}
                                        >
                                            {playingFile === rec.filename ? '⏹ Stop' : '▶ Play'}
                                        </button>
                                        <a
                                            href={`${API}/recordings/${rec.filename}`}
                                            download={rec.filename}
                                            title="Download"
                                            style={{
                                                padding: '6px 14px', borderRadius: '6px',
                                                background: 'rgba(0, 230, 118, 0.08)',
                                                border: '1px solid rgba(0, 230, 118, 0.3)',
                                                color: 'var(--green-online)', cursor: 'pointer',
                                                fontSize: '0.8rem', fontFamily: 'var(--font-mono)',
                                                textDecoration: 'none', display: 'flex', alignItems: 'center'
                                            }}
                                        >
                                            ↓ Download
                                        </a>
                                        <button
                                            onClick={() => deleteRecording(rec.filename)}
                                            title="Delete"
                                            style={{
                                                padding: '6px 14px', borderRadius: '6px',
                                                background: 'rgba(255, 23, 68, 0.08)',
                                                border: '1px solid rgba(255, 23, 68, 0.3)',
                                                color: 'var(--red-alert)', cursor: 'pointer',
                                                fontSize: '0.8rem', fontFamily: 'var(--font-mono)',
                                                transition: 'all 0.2s ease'
                                            }}
                                        >
                                            🗑 Delete
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

// ─── Main VideoFeed Component ─────────────────────────────────────────────────
const VideoFeed = () => {
    const [size, setSize] = useState('medium');
    const [isFullscreen, setIsFullscreen] = useState(false);
    const [isRecording, setIsRecording] = useState(false);
    const [elapsed, setElapsed] = useState(0);
    const [showLibrary, setShowLibrary] = useState(false);
    const [recError, setRecError] = useState(null);

    const containerRef = useRef(null);
    const timerRef = useRef(null);

    // Sync recording state with backend on mount
    useEffect(() => {
        fetch(`${API}/recording_status`)
            .then(r => r.json())
            .then(d => {
                if (d.active) {
                    setIsRecording(true);
                    setElapsed(d.elapsed || 0);
                }
            })
            .catch(console.error);
    }, []);

    // Live timer while recording
    useEffect(() => {
        if (isRecording) {
            timerRef.current = setInterval(() => setElapsed(prev => prev + 1), 1000);
        } else {
            clearInterval(timerRef.current);
        }
        return () => clearInterval(timerRef.current);
    }, [isRecording]);

    // Fullscreen listener
    useEffect(() => {
        const handler = () => setIsFullscreen(!!document.fullscreenElement);
        document.addEventListener('fullscreenchange', handler);
        return () => document.removeEventListener('fullscreenchange', handler);
    }, []);

    const handleFullscreen = () => {
        if (!document.fullscreenElement) {
            const el = containerRef.current;
            if (el.requestFullscreen) el.requestFullscreen();
            else if (el.mozRequestFullScreen) el.mozRequestFullScreen();
            else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
            else if (el.msRequestFullscreen) el.msRequestFullscreen();
        } else {
            document.exitFullscreen();
        }
    };

    const handleRecordToggle = async () => {
        setRecError(null);
        if (!isRecording) {
            try {
                const res = await fetch(`${API}/start_recording`, { method: 'POST' });
                const data = await res.json();
                if (data.status === 'success') {
                    setIsRecording(true);
                    setElapsed(0);
                } else {
                    setRecError(data.message || 'Failed to start recording');
                }
            } catch (e) {
                setRecError('Could not connect to backend');
            }
        } else {
            try {
                const res = await fetch(`${API}/stop_recording`, { method: 'POST' });
                const data = await res.json();
                if (data.status === 'success') {
                    setIsRecording(false);
                    setElapsed(0);
                } else {
                    setRecError(data.message || 'Failed to stop recording');
                }
            } catch (e) {
                setRecError('Could not connect to backend');
            }
        }
    };

    const getContainerHeight = () => {
        if (isFullscreen) return '100vh';
        switch (size) {
            case 'small': return '300px';
            case 'large': return '800px';
            case 'medium':
            default: return '500px';
        }
    };

    const sizeBtn = (targetSize) => ({
        padding: '6px 12px',
        background: size === targetSize ? 'var(--accent-blue)' : 'rgba(59, 130, 246, 0.1)',
        color: size === targetSize ? '#ffffff' : 'var(--text-primary)',
        border: '1px solid rgba(59, 130, 246, 0.3)',
        borderRadius: '6px', cursor: 'pointer',
        fontSize: '0.875rem', fontWeight: '600',
        transition: 'all 0.2s ease',
        fontFamily: 'var(--font-mono)'
    });

    return (
        <div style={{ display: 'flex', flexDirection: 'column', height: '100%', width: '100%' }}>
            {/* Title row */}
            <div style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                marginBottom: '1.25rem', flexWrap: 'wrap', gap: '10px'
            }}>
                <h2 className="section-header" style={{ marginBottom: 0 }}>
                    <span role="img" aria-label="camera">📷</span>{" "}
                    Live Video Feed
                    {isRecording && (
                        <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '6px',
                            marginLeft: '16px', fontSize: '0.7rem',
                            padding: '3px 10px', borderRadius: '12px',
                            background: 'rgba(255, 23, 68, 0.15)',
                            border: '1px solid rgba(255, 23, 68, 0.5)',
                            color: 'var(--red-alert)',
                            fontFamily: 'var(--font-mono)', letterSpacing: '0.1em',
                            animation: 'recBlink 1.2s ease-in-out infinite'
                        }}>
                            <span style={{
                                width: '7px', height: '7px', borderRadius: '50%',
                                background: 'var(--red-alert)',
                                boxShadow: '0 0 6px var(--red-alert)'
                            }} />
                            REC {fmtElapsed(elapsed)}
                        </span>
                    )}
                </h2>

                <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
                    {/* Size buttons */}
                    <button className="fancy-button" style={sizeBtn('small')} onClick={() => setSize('small')}>Small</button>
                    <button className="fancy-button" style={sizeBtn('medium')} onClick={() => setSize('medium')}>Medium</button>
                    <button className="fancy-button" style={sizeBtn('large')} onClick={() => setSize('large')}>Large</button>

                    {/* Fullscreen */}
                    <button
                        className="fancy-button"
                        onClick={handleFullscreen}
                        style={{
                            padding: '6px 12px', borderRadius: '6px',
                            background: 'rgba(59, 130, 246, 0.2)',
                            border: '1px solid rgba(59, 130, 246, 0.3)',
                            color: 'var(--text-primary)', cursor: 'pointer',
                            fontSize: '0.875rem', fontWeight: '600',
                            transition: 'all 0.2s ease', fontFamily: 'var(--font-mono)'
                        }}
                    >
                        ⛶ Fullscreen
                    </button>

                    {/* ─── RECORD BUTTON ─── */}
                    <button
                        id="record-btn"
                        onClick={handleRecordToggle}
                        title={isRecording ? 'Stop Recording' : 'Start Recording'}
                        style={{
                            padding: '6px 16px', borderRadius: '6px',
                            background: isRecording
                                ? 'rgba(255, 23, 68, 0.2)'
                                : 'rgba(255, 23, 68, 0.08)',
                            border: `1px solid ${isRecording ? 'var(--red-alert)' : 'rgba(255,23,68,0.4)'}`,
                            color: 'var(--red-alert)', cursor: 'pointer',
                            fontSize: '0.875rem', fontWeight: '700',
                            transition: 'all 0.2s ease', fontFamily: 'var(--font-mono)',
                            display: 'flex', alignItems: 'center', gap: '8px',
                            boxShadow: isRecording ? '0 0 12px rgba(255,23,68,0.35)' : 'none',
                            letterSpacing: '0.05em'
                        }}
                    >
                        <span style={{
                            width: '9px', height: '9px', borderRadius: '50%',
                            background: 'var(--red-alert)',
                            boxShadow: isRecording ? '0 0 8px var(--red-alert)' : 'none',
                            animation: isRecording ? 'recBlink 1.2s ease-in-out infinite' : 'none',
                            flexShrink: 0
                        }} />
                        {isRecording ? `Stop Rec` : 'REC'}
                    </button>

                    {/* Library button */}
                    <button
                        id="recordings-library-btn"
                        onClick={() => setShowLibrary(true)}
                        title="View Recordings"
                        style={{
                            padding: '6px 14px', borderRadius: '6px',
                            background: 'rgba(0, 229, 255, 0.08)',
                            border: '1px solid rgba(0,229,255,0.3)',
                            color: 'var(--cyan-primary)', cursor: 'pointer',
                            fontSize: '0.875rem', fontWeight: '600',
                            transition: 'all 0.2s ease', fontFamily: 'var(--font-mono)'
                        }}
                    >
                        🎬 Library
                    </button>
                </div>
            </div>

            {/* Error banner */}
            {recError && (
                <div style={{
                    marginBottom: '10px', padding: '8px 14px', borderRadius: '6px',
                    background: 'rgba(255,23,68,0.1)', border: '1px solid rgba(255,23,68,0.4)',
                    color: 'var(--red-alert)', fontFamily: 'var(--font-mono)', fontSize: '0.8rem',
                    display: 'flex', justifyContent: 'space-between', alignItems: 'center'
                }}>
                    ⚠️ {recError}
                    <button onClick={() => setRecError(null)} style={{
                        background: 'none', border: 'none', color: 'var(--red-alert)',
                        cursor: 'pointer', fontSize: '1rem'
                    }}>✕</button>
                </div>
            )}

            {/* Video container */}
            <div
                ref={containerRef}
                className={`card video-card-hover ${!isFullscreen ? 'animate-slide-up delay-100' : ''}`}
                style={{
                    padding: 0, overflow: 'hidden',
                    display: 'flex', justifyContent: 'center', alignItems: 'center',
                    backgroundColor: '#000',
                    transition: 'all 0.3s ease',
                    width: '100%', height: getContainerHeight(),
                    borderRadius: isFullscreen ? '0' : '16px',
                    border: isFullscreen ? 'none' : undefined,
                    position: 'relative'
                }}
            >
                <img
                    src={`${API}/video_feed`}
                    alt="Live Video Feed"
                    style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }}
                />

                {/* REC overlay on video */}
                {isRecording && (
                    <div style={{
                        position: 'absolute', top: '14px', right: '16px',
                        display: 'flex', alignItems: 'center', gap: '7px',
                        padding: '5px 12px', borderRadius: '20px',
                        background: 'rgba(0,0,0,0.7)',
                        border: '1px solid rgba(255,23,68,0.6)',
                        backdropFilter: 'blur(6px)'
                    }}>
                        <span style={{
                            width: '9px', height: '9px', borderRadius: '50%',
                            background: '#ff1744',
                            boxShadow: '0 0 8px #ff1744',
                            animation: 'recBlink 1s ease-in-out infinite'
                        }} />
                        <span style={{
                            fontFamily: 'var(--font-mono)', fontSize: '0.78rem',
                            color: '#ff6090', letterSpacing: '0.12em', fontWeight: '700'
                        }}>
                            REC {fmtElapsed(elapsed)}
                        </span>
                    </div>
                )}
            </div>

            {/* Recordings Library Modal */}
            {showLibrary && <RecordingsLibrary onClose={() => setShowLibrary(false)} />}
        </div>
    );
};

export default VideoFeed;
