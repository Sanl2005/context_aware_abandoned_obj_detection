import React from 'react';
import './VideoFeed.css';

const VideoFeed = ({ streamUrl = 'http://127.0.0.1:5000/video_feed' }) => {
    return (
        <div className="video-feed-container">
            <div className="video-header">
                <div className="video-title">
                    <span role="img" aria-label="camera">📹</span> Live Object Detection
                </div>
                <div className="recording-indicator">
                    <div className="recording-dot"></div>
                    <span>LIVE</span>
                </div>
            </div>
            <div className="video-wrapper">
                <img
                    src={streamUrl}
                    alt="Live object detection feed"
                    className="video-stream"
                />
            </div>
            <div className="video-info">
                <span className="info-badge">
                    <span role="img" aria-label="eye">👁️</span> Monitoring
                </span>
                <span className="info-badge">
                    <span role="img" aria-label="robot">🤖</span> AI Detection Active
                </span>
            </div>
        </div>
    );
};

export default VideoFeed;
