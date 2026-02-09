# Object Detection Integration Setup Guide

## Overview
This integration adds a live video feed with real-time object detection to the frontend dashboard. The video stream displays:
- Live webcam feed with bounding boxes around detected objects
- Different colors for varying confidence levels (green for high, orange for medium)
- Red warnings for abandoned objects (stationary for >5 seconds)
- Object labels with confidence scores

## Setup Instructions

### 1. Install Backend Dependencies

Navigate to the `ml_service` directory and install the required packages:

```bash
cd ml_service
pip install flask-cors
```

Or install all requirements:
```bash
pip install -r requirements.txt
```

### 2. Start the ML Service (Backend)

Start the Flask server that will stream the video feed:

```bash
# From the ml_service directory
python app.py
```

The server will start on `http://127.0.0.1:5000`

**Important endpoints:**
- `GET /status` - Check if the service is running
- `GET /video_feed` - Live video stream with object detection
- `POST /detect` - Image upload for single-frame detection

### 3. Start the Rails Backend (if needed)

The system also requires the Rails backend for storing detection data:

```bash
cd rails_backend
rails server -p 3000
```

### 4. Start the Frontend Dashboard

In a new terminal, navigate to the frontend directory:

```bash
cd frontend_dashboard
npm start
```

The dashboard will open at `http://localhost:3000`

## Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React)       │
│   Port: 3000    │
└────────┬────────┘
         │
         ├──────────────────────┐
         │                      │
         ▼                      ▼
┌─────────────────┐    ┌─────────────────┐
│  ML Service     │    │  Rails Backend  │
│  (Flask)        │◄───│  (API)          │
│  Port: 5000     │    │  Port: 3000     │
│                 │    │                 │
│ - Video Feed    │    │ - Detections DB │
│ - YOLO Model    │    │ - Alerts        │
│ - Object Track  │    │ - Risk Analysis │
└─────────────────┘    └─────────────────┘
```

## Features

### Live Video Feed Component
- **Location**: `frontend_dashboard/src/components/VideoFeed.js`
- **Styling**: Modern dark theme with glassmorphism effects
- **Indicators**: 
  - Live recording indicator with pulsing animation
  - Monitoring and AI status badges

### Backend Video Streaming
- **Endpoint**: `/video_feed` in `ml_service/app.py`
- **Format**: MJPEG (Motion JPEG) stream
- **Features**:
  - Real-time YOLO object detection
  - Object tracking for abandoned object detection
  - Configurable object classes (person, handbag, backpack, laptop, etc.)
  - Automatic bounding box drawing with confidence scores

### Object Tracking
- Uses the existing `ObjectTracker` from `ml_service/utils/object_tracker.py`
- Tracks objects across frames
- Detects stationary objects (potential abandoned items)
- Threshold: 5 seconds for demo (configurable)

## Customization

### Change Camera Source
Edit `ml_service/app.py`:
```python
def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)  # Change 0 to video file path or different camera ID
    return camera
```

### Adjust Abandoned Object Threshold
Edit `ml_service/app.py` in the `generate_frames()` function:
```python
if obj.stationary_time > 5:  # Change from 5 to desired seconds
```

### Add/Remove Tracked Object Classes
Edit the object class list in `generate_frames()`:
```python
if name in ["person", "handbag", "backpack", ...]:  # Add or remove classes
```

## Troubleshooting

### Video feed not loading
1. Ensure ML service is running on port 5000
2. Check browser console for CORS errors
3. Verify webcam permissions are granted
4. Check if webcam is already in use by another application

### Performance Issues
1. The YOLO model (`yolov8n.pt`) is the nano version for speed
2. For better accuracy, use `yolov8s.pt` or `yolov8m.pt` (slower)
3. Reduce video resolution in the camera settings
4. Increase frame skip interval if needed

### CORS Errors
- Ensure `flask-cors` is installed
- Check that `CORS(app)` is called in `app.py`

## Next Steps

- Add recording functionality to save video clips with detections
- Implement zone-based monitoring (restrict detection to specific areas)
- Add notification system for real-time alerts
- Integrate with mobile app for remote monitoring
- Add support for multiple camera feeds
