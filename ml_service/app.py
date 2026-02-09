from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from ultralytics import YOLO
import requests
import datetime
import os
import cv2

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

# Load YOLO model (small + fast)
model = YOLO("yolov8n.pt")

RAILS_API = "http://127.0.0.1:3000/api/detected_objects"

# Video capture instance (webcam)
camera = None

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    return camera

def generate_frames():
    """Generator function that yields frames with object detection overlay"""
    print("[VIDEO_FEED] Starting video feed stream...")
    
    try:
        cam = get_camera()
        
        if not cam.isOpened():
            print("[ERROR] Camera is not opened!")
            return
        
        print("[VIDEO_FEED] Camera opened successfully")
        
        # Track objects for abandoned detection
        try:
            from utils.object_tracker import ObjectTracker
            tracker = ObjectTracker()
            print("[VIDEO_FEED] Object tracker initialized")
        except Exception as e:
            print(f"[WARNING] Could not initialize tracker: {e}")
            tracker = None
        
        frame_count = 0
        
        while True:
            try:
                success, frame = cam.read()
                
                if not success or frame is None:
                    print("[ERROR] Failed to read frame from camera")
                    break
                
                frame_count += 1
                if frame_count % 30 == 0:  # Log every 30 frames
                    print(f"[VIDEO_FEED] Processed {frame_count} frames")
                
                # Run YOLO detection
                try:
                    results = model(frame, verbose=False)
                    
                    detections = []
                    for r in results:
                        if r.boxes is None:
                            continue
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            conf = float(box.conf[0])
                            name = model.names[cls_id]
                            x1, y1, x2, y2 = box.xyxy[0].tolist()
                            
                            detections.append({
                                'class_name': name,
                                'confidence': conf,
                                'bbox': [x1, y1, x2, y2]
                            })
                            
                            # Draw bounding box
                            if name in ["person", "handbag", "backpack", "suitcase", "cell phone", 
                                       "teddy bear", "chair", "tv", "remote", "keyboard", "mouse", 
                                       "book", "laptop", "bottle"]:
                                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                                
                                # Different color for high confidence
                                color = (0, 255, 0) if conf > 0.7 else (0, 165, 255)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                                
                                # Label with confidence
                                label = f'{name} {conf:.2f}'
                                cv2.putText(frame, label, (x1, y1 - 10),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                    
                    # Update tracker if available
                    if tracker:
                        tracked_objects = tracker.update(detections)
                        
                        # Draw abandoned object warnings
                        for obj in tracked_objects:
                            if obj.stationary_time > 5:  # 5 seconds threshold for demo
                                # Draw red warning box
                                x1, y1, x2, y2 = map(int, obj.last_bbox)
                                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                                cv2.putText(frame, f'ABANDONED! ({obj.stationary_time:.1f}s)', 
                                          (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                
                except Exception as e:
                    print(f"[ERROR] Detection error: {e}")
                    # Continue even if detection fails
                
                # Encode frame as JPEG
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    print("[ERROR] Failed to encode frame")
                    continue
                    
                frame_bytes = buffer.tobytes()
                
                # Yield frame in multipart format
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
                       
            except Exception as e:
                print(f"[ERROR] Error in frame processing loop: {e}")
                import traceback
                traceback.print_exc()
                break
                
    except Exception as e:
        print(f"[FATAL ERROR] Video feed error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[VIDEO_FEED] Stream ended")


@app.get("/status")
def status():
    return jsonify({"status": "ok", "message": "Flask ML Service running"})


@app.get("/video_feed")
def video_feed():
    """Video streaming route. Returns a multipart response with JPEG frames."""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')



@app.post("/detect")
def detect():
    if "image" not in request.files:
        return jsonify({"error": "No image file provided. Use form-data key = image"}), 400

    image_file = request.files["image"]

    # Save temporarily
    os.makedirs("uploads", exist_ok=True)
    img_path = os.path.join("uploads", image_file.filename)
    image_file.save(img_path)

    # Run YOLO
    results = model(img_path)

    detections = []
    for r in results:
        if r.boxes is None:
            continue
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            name = model.names[cls_id]

            x1, y1, x2, y2 = box.xyxy[0].tolist()
            bbox = [round(x1, 2), round(y1, 2), round(x2, 2), round(y2, 2)]

            detections.append({
                "object_type": name,
                "confidence": conf,
                "bbox": bbox
            })

    # For demo: if ANY detection exists → send first one to Rails
    if len(detections) > 0:
        first = detections[0]

        payload = {
            "detected_object": {
                "track_id": "YOLO_IMG_001",
                "object_type": first["object_type"],
                "confidence": first["confidence"],
                "bbox": str(first["bbox"]),
                "first_seen_at": datetime.datetime.utcnow().isoformat(),
                "last_seen_at": datetime.datetime.utcnow().isoformat(),
                "status": "abandoned",   # demo trigger alert
                "camera_source_id": 1
            }
        }

        try:
            res = requests.post(RAILS_API, json=payload)
            rails_status = res.status_code
            rails_response = res.json()
        except Exception as e:
            rails_status = "failed"
            rails_response = str(e)

        return jsonify({
            "detections": detections,
            "sent_to_rails": True,
            "rails_status": rails_status,
            "rails_response": rails_response
        })

    return jsonify({"detections": [], "sent_to_rails": False})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
