# System Architecture - Object Detection Dashboard

## High-Level Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                          USER BROWSER                            │
│                     http://localhost:3001                        │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                    REACT FRONTEND DASHBOARD                      │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Header: "SentinelEye Dashboard" + Live Indicator          │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  VideoFeed Component                                       │ │
│  │  • Displays: http://127.0.0.1:5000/video_feed             │ │
│  │  • Live video stream with bounding boxes                  │ │
│  │  • Shows: object labels, confidence, abandoned warnings   │ │
│  └────────────────────────────────────────────────────────────┘ │
│                                                                  │
│  ┌─────────────────────┐  ┌────────────────────────────────────┐ │
│  │ Detected Objects    │  │ Alerts & Risk Analysis            │ │
│  │ (from Rails API)    │  │ (from Rails API)                  │ │
│  └─────────────────────┘  └────────────────────────────────────┘ │
└──────────────┬────────────────────────────┬──────────────────────┘
               │ axios GET                  │ axios GET
               │ /api/detected_objects      │ /api/alerts
               │ /api/risk_assessments      │
               ▼                            │
┌────────────────────────────┐             │
│   RAILS BACKEND (API)      │◄────────────┘
│   Port: 3000               │
│                            │
│  • Stores detected objects │◄──────────────┐
│  • Manages alerts          │               │
│  • Risk assessments        │               │
│  • PostgreSQL database     │               │ POST detections
└────────────────────────────┘               │
                                             │
                             ┌───────────────┴──────────────────┐
                             │  ML SERVICE (Flask)              │
                             │  Port: 5000                      │
                             │                                  │
                             │  Endpoints:                      │
                             │  • GET /video_feed               │
                             │  • GET /status                   │
                             │  • POST /detect                  │
                             │                                  │
                             │  Components:                     │
                             │  ┌────────────────────────────┐  │
                             │  │ Camera Manager             │  │
                             │  │ • cv2.VideoCapture(0)      │  │
                             │  └──────────┬─────────────────┘  │
                             │             ▼                    │
                             │  ┌────────────────────────────┐  │
                             │  │ Frame Generator            │  │
                             │  │ • Captures frames          │  │
                             │  │ • Runs YOLO detection      │  │
                             │  │ • Draws bounding boxes     │  │
                             │  └──────────┬─────────────────┘  │
                             │             ▼                    │
                             │  ┌────────────────────────────┐  │
                             │  │ YOLO Detector              │  │
                             │  │ • Model: yolov8n.pt        │  │
                             │  │ • Detects 80 object types  │  │
                             │  └──────────┬─────────────────┘  │
                             │             ▼                    │
                             │  ┌────────────────────────────┐  │
                             │  │ Object Tracker             │  │
                             │  │ • Tracks objects           │  │
                             │  │ • Detects stationary items │  │
                             │  │ • Abandoned detection      │  │
                             │  └──────────┬─────────────────┘  │
                             │             ▼                    │
                             │  ┌────────────────────────────┐  │
                             │  │ MJPEG Stream Encoder       │  │
                             │  │ • Encodes frame as JPEG    │  │
                             │  │ • Streams to frontend      │  │
                             │  └────────────────────────────┘  │
                             └──────────────────────────────────┘
                                             ▲
                                             │
                                   ┌─────────┴─────────┐
                                   │  WEBCAM (Video)   │
                                   │  Camera ID: 0     │
                                   └───────────────────┘
```

## Data Flow

### 1. Video Streaming Flow
```
Webcam → ML Service → Frame Capture → YOLO Detection → 
Draw Boxes → Object Tracking → JPEG Encoding → 
MJPEG Stream → Frontend <img> Tag → User Browser
```

### 2. Detection Data Flow
```
YOLO Detection → POST to Rails API → Database → 
Frontend axios GET → Display in Cards
```

### 3. Alert Generation Flow
```
Object Tracker → Detects Abandoned Object → 
POST Alert to Rails → Database → 
Frontend axios GET → Display in Alerts Panel
```

## Component Breakdown

### Frontend Components

```
src/
├── App.js                 # Main dashboard orchestrator
├── App.css               # Dashboard styling
├── components/
│   ├── VideoFeed.js      # Video stream display component
│   ├── VideoFeed.css     # Video feed styling
│   ├── Navbar.js         # Navigation (existing)
│   ├── AlertsTable.js    # Alerts display (existing)
│   └── DetectedObjectsTable.js  # Objects grid (existing)
└── api/
    ├── api.js            # API client
    └── detectedObjects.js # API endpoints
```

### Backend Components (ML Service)

```
ml_service/
├── app.py                # Flask server + video streaming
├── models/
│   └── yolo_detector.py  # YOLO model wrapper
├── utils/
│   └── object_tracker.py # Object tracking logic
├── video/
│   └── video_reader.py   # Video capture wrapper
└── pipeline/
    └── run_pipeline.py   # Standalone detection (cv2.imshow)
```

## Technology Stack

### Frontend
- **Framework**: React 19.2.3
- **HTTP Client**: Axios
- **Routing**: React Router DOM
- **Styling**: CSS3 (Modern Dark Theme)

### ML Service
- **Framework**: Flask + flask-cors
- **Computer Vision**: OpenCV (cv2)
- **Object Detection**: YOLOv8 (Ultralytics)
- **Deep Learning**: PyTorch
- **Video Codec**: MJPEG (Motion JPEG)

### Backend API
- **Framework**: Ruby on Rails
- **Database**: PostgreSQL
- **API Format**: JSON REST

## Network Topology

```
┌─────────────┐
│   Browser   │  
│  :3001      │  
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌──────────┐      ┌──────────┐
│  Flask   │      │  Rails   │
│  :5000   │───────▶  :3000   │
└──────────┘      └──────────┘
     │                  │
     ▼                  ▼
  Webcam          PostgreSQL
```

## Request/Response Examples

### Video Feed Request
```http
GET http://127.0.0.1:5000/video_feed
Accept: */*

Response:
Content-Type: multipart/x-mixed-replace; boundary=frame

--frame
Content-Type: image/jpeg

[JPEG DATA]
--frame
Content-Type: image/jpeg

[JPEG DATA]
...
```

### Detection Data Request
```http
GET http://127.0.0.1:3000/api/detected_objects
Accept: application/json

Response:
[
  {
    "id": 1,
    "object_type": "person",
    "confidence": 0.92,
    "status": "detected",
    "camera_source_id": 1,
    "last_seen_at": "2026-02-09T12:34:56Z"
  },
  ...
]
```

## Deployment Ports

| Service | Port | Protocol | Purpose |
|---------|------|----------|---------|
| Frontend | 3001 | HTTP | React dashboard |
| Rails API | 3000 | HTTP | REST API |
| ML Service | 5000 | HTTP | Video streaming + Detection |
| PostgreSQL | 5432 | TCP | Database (Rails) |

## Security Considerations

1. **CORS**: Enabled on ML Service for localhost origins
2. **Webcam Access**: Requires user permission in browser
3. **Network**: Currently localhost-only (not production-ready)
4. **HTTPS**: Required for webcam access on non-localhost
5. **Authentication**: Not implemented (add for production)

## Performance Metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Video Latency | <500ms | Typical MJPEG delay |
| Detection FPS | 15-30 | Depends on hardware |
| Model Load Time | 2-5s | On first request |
| API Response | <100ms | Rails endpoints |
| Memory Usage | ~500MB | ML Service typical |

## Scalability Considerations

### Current Limitations
- Single camera support
- No load balancing
- Local processing only
- No video recording storage

### Future Enhancements
- Multi-camera support
- Cloud-based processing
- Distributed detection
- Video archive storage
- Load balancer for ML Service
- Microservices architecture
