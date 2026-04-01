from flask import Flask, request, jsonify, Response, send_from_directory
from flask_cors import CORS
from ultralytics import YOLO
import requests
import datetime
import os
import cv2
import json
import torch
import threading
import time

from database import init_db, get_db_session, ObjectAlert
from alert_service import alert_tracker  # SOS email/SMS alerts

# ─── Recording State ─────────────────────────────────────────────────────────
RECORDINGS_DIR = os.path.join(os.path.dirname(__file__), "recordings")
os.makedirs(RECORDINGS_DIR, exist_ok=True)

recording_state = {
    "active": False,
    "filename": None,
    "start_time": None,
    "writer": None,
    "thread": None,
}
recording_lock = threading.Lock()
# ─────────────────────────────────────────────────────────────────────────────

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend access

init_db() # Run DB initialization


# ─── Model Configuration ─────────────────────────────────────────────────────
# YOLOv26x: Extra-Large variant — highest accuracy in the YOLOv26 family
# NMS-free, DFL-free, STAL small-object-aware, MuSGD trained
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"[INFO] Using device: {DEVICE.upper()}")

custom_model_path = "runs/train/abandoned_object_detection/weights/best.pt"
if os.path.exists(custom_model_path):
    print(f"[INFO] Loading custom fine-tuned model from {custom_model_path}")
    model = YOLO(custom_model_path)
else:
    print("[INFO] Loading YOLOv26x (Extra-Large) — best accuracy model")
    model = YOLO("yolo26x.pt")

# Move model to GPU if available and use FP16 for speed
if DEVICE == "cuda":
    model.to(DEVICE)
    print("[INFO] YOLOv26x loaded on GPU (CUDA) with FP16 half-precision")
else:
    print("[INFO] YOLOv26x loaded on CPU — consider GPU for real-time performance")
# ─────────────────────────────────────────────────────────────────────────────
latest_processed_frame = None

# New Endpoint for full ML results
RAILS_API_RESULTS = "http://127.0.0.1:3000/api/ml_results"

# Video capture instance (webcam)
camera = None

def get_camera():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    return camera

# Global tracker reference for API access
tracker_instance = None

def generate_frames():
    global tracker_instance
    """Generator function that yields frames with object detection overlay"""
    print("[VIDEO_FEED] Starting video feed stream...")
    
    try:
        cam = get_camera()
        
        if not cam.isOpened():
            print("[ERROR] Camera is not opened!")
            return
        
        print("[VIDEO_FEED] Camera opened successfully")
        
        # Initialize Advanced Object Tracker
        try:
            from utils.object_tracker import ObjectTracker
            # Default location type for now - in production this comes from config or DB per camera
            if tracker_instance is None:
                tracker_instance = ObjectTracker(location_type="PUBLIC_OPEN_CROWDED") 
            tracker = tracker_instance
            print("[VIDEO_FEED] Advanced Object tracker initialized")
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
                
                # Run YOLO detection with YOLOv26x
                try:
                    results = model(
                        frame,
                        verbose=False,
                        device=DEVICE,
                        half=(DEVICE == "cuda"),  # FP16 on GPU for speed
                        imgsz=640                 # Input resolution
                    )
                    
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

                    # Update tracker
                    tracked_objects = []
                    if tracker:
                        tracked_objects = tracker.update(detections)
                        
                        # Map dynamic ML location to valid Rails enum
                        mapped_location = "public_open_crowded"  # Default fallback
                        loc = tracker.location_context.location_type.upper()
                        if "RESTRICTED" in loc: mapped_location = "semi_restricted_zone"
                        elif "REMOTE" in loc: mapped_location = "public_remote_area"

                        # Prepare payload for Rails
                        ml_payload = {
                            "camera_id": 1,
                            "location_type": mapped_location,
                            "crowd_density": tracker.crowd_analyzer.current_density,
                            "objects": []
                        }

                        # Draw detections & Warnings
                        # VISUALIZATION OF "INTELLIGENCE"
                        # 1. Location Awareness
                        cv2.putText(frame, f"Location: {tracker.location_context.location_type}", (10, 30),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
                        
                        # 2. Crowd Adaptivity
                        cv2.putText(frame, f"Crowd Density: {tracker.crowd_analyzer.current_density} ppl", (10, 60),
                                  cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                        # Create a dictionary of current person crops so objects can link to them even after they leave
                        if not hasattr(tracker, 'person_crops_cache'):
                            tracker.person_crops_cache = {}

                        for obj in tracked_objects:
                            if obj.class_name == "person":
                                x1, y1, x2, y2 = map(int, obj.bbox)
                                h, w = frame.shape[:2]
                                cy1, cy2 = max(0, y1), min(h, y2)
                                cx1, cx2 = max(0, x1), min(w, x2)
                                p_crop = frame[cy1:cy2, cx1:cx2]
                                if p_crop.size > 0:
                                    import base64
                                    _, buffer = cv2.imencode('.jpg', p_crop)
                                    tracker.person_crops_cache[obj.id] = "data:image/jpeg;base64," + base64.b64encode(buffer.tobytes()).decode('utf-8')

                        for obj in tracked_objects:
                            x1, y1, x2, y2 = map(int, obj.bbox)
                            
                            # Color based on Threat Level
                            color = (0, 255, 0) # Green (Low)
                            if obj.threat_level == "MEDIUM_RISK":
                                color = (0, 165, 255) # Orange
                            elif obj.threat_level == "HIGH_RISK":
                                color = (0, 0, 255) # Red
                            
                            # Draw Box
                            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                            
                            # 3. Threat-Aware & Behavior-Intelligent Labels
                            # Show comprehensive status: Class | ID | STATE
                            if obj.class_name == "person":
                                label = f'Person ID:{obj.id} | {obj.state}'
                            else:
                                owner_str = f"Owner:{obj.owner_id}" if getattr(obj, "owner_id", None) else "No Owner"
                                label = f'{obj.class_name.upper()} ID:{obj.id} | {owner_str} | Risk:{obj.abandonment_confidence:.1f} | {obj.state}'
                            
                            # Make text slightly smaller so it fits
                            cv2.putText(frame, label, (x1, y1 - 8),
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 2)

                            # Abandonment Warning
                            if obj.abandonment_confidence > 0.8:
                                cv2.putText(frame, "ABANDONED!", (x1, y1 - 30),
                                          cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

                            # Image capture for alerts
                            import base64
                            object_image_base64 = ""
                            person_image_base64 = ""
                            owner_id = getattr(obj, "owner_id", None)
                            
                            if not hasattr(obj, "best_object_crop"):
                                obj.best_object_crop = ""
                            
                            # Always update object crop when visible
                            try:
                                h, w = frame.shape[:2]
                                cy1, cy2 = max(0, y1), min(h, y2)
                                cx1, cx2 = max(0, x1), min(w, x2)
                                obj_crop = frame[cy1:cy2, cx1:cx2]
                                if obj_crop.size > 0:
                                    _, obuffer = cv2.imencode('.jpg', obj_crop)
                                    obj.best_object_crop = "data:image/jpeg;base64," + base64.b64encode(obuffer.tobytes()).decode('utf-8')
                            except:
                                pass
                                
                            # Capture images for any object with confidence > 0.7 (not just > 0.8)
                            if obj.abandonment_confidence > 0.7:
                                object_image_base64 = getattr(obj, "best_object_crop", "")
                                if owner_id and hasattr(tracker, 'person_crops_cache'):
                                    person_image_base64 = tracker.person_crops_cache.get(owner_id, "")
                                # If still no person image but we have a cache, try the most recently seen person
                                if not person_image_base64 and hasattr(tracker, 'person_crops_cache') and tracker.person_crops_cache:
                                    # Use most recently cached person as a fallback
                                    person_image_base64 = list(tracker.person_crops_cache.values())[-1]

                            # Populate payload
                            payload_obj = {
                                "object_id": obj.id,
                                "class_name": obj.class_name,
                                "state": obj.state,
                                "threat_level": obj.threat_level,
                                "confidence": obj.abandonment_confidence,
                                "bbox": obj.bbox,
                                "stationary_time": obj.stationary_time,
                                "owner_id": owner_id,
                                "object_image_base64": object_image_base64,
                                "person_image_base64": person_image_base64,
                                "is_alert": obj.abandonment_confidence > 0.8
                            }
                            ml_payload["objects"].append(payload_obj)
                            
                            if payload_obj["is_alert"]:
                                print(f"[DEBUG] Abandoned alert appending: obj={len(object_image_base64)} chars, person={len(person_image_base64)} chars, owner_id={owner_id}")
                                # ── SOS Alert: send email/SMS if sustained >10s ──
                                alert_tracker.check_and_send(
                                    object_id=str(obj.id),
                                    class_name=obj.class_name,
                                    confidence=obj.abandonment_confidence,
                                    stationary_time=obj.stationary_time,
                                    location_type=ml_payload.get("location_type", "UNKNOWN")
                                )
                        
                        # Send to Rails periodically (e.g., every 30 frames or on high risk)
                        # For demo, let's send if any high confidence object exists
                        should_send = any(o["confidence"] > 0.7 for o in ml_payload["objects"])
                        
                        if should_send and frame_count % 15 == 0: # Rate limit
                                # Save to Postgres DB
                                try:
                                    session = get_db_session()
                                    if session:
                                        for obj in ml_payload["objects"]:
                                            if obj["threat_level"] in ["HIGH_RISK", "MEDIUM_RISK"] or obj["confidence"] > 0.7:
                                                new_alert = ObjectAlert(
                                                    object_id=str(obj["object_id"]),
                                                    class_name=obj["class_name"],
                                                    state=obj["state"],
                                                    threat_level=obj["threat_level"],
                                                    confidence=float(obj["confidence"]),
                                                    stationary_time=float(obj["stationary_time"]),
                                                    location_type=ml_payload["location_type"],
                                                    crowd_density=int(ml_payload["crowd_density"]),
                                                    owner_id=obj.get("owner_id"),
                                                    object_image_base64=obj.get("object_image_base64"),
                                                    person_image_base64=obj.get("person_image_base64")
                                                )
                                                session.add(new_alert)
                                        session.commit()
                                        session.close()
                                except Exception as e:
                                    print(f"[ERROR] DB insert failed: {e}")

                                try:
                                    requests.post(RAILS_API_RESULTS, json=ml_payload, timeout=1.0)
                                    print(f"[sending to rails] Abandoned items processed")
                                except Exception as e:
                                    print(f"[ERROR] Rails update failed: {e}")

                except Exception as e:
                    print(f"[ERROR] Detection logic error: {e}")
                    import traceback
                    traceback.print_exc()

                global latest_processed_frame
                latest_processed_frame = frame.copy()

                # Encode frame
                ret, buffer = cv2.imencode('.jpg', frame)
                if not ret:
                    continue
                
                # Debug: Log every 30 frames
                if frame_count % 30 == 0:
                    print(f"[DEBUG] Sending frame {frame_count} ({len(buffer)} bytes)")
                    
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
                       
            except Exception as e:
                print(f"[ERROR] Frame loop error: {e}")
                break
                
    except Exception as e:
        print(f"[FATAL] Video feed setup error: {e}")
    finally:
        pass

@app.get("/video_feed")
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.get("/status")
def status():
    # Gather active logic details
    logic_status = {
        "status": "ok",
        "message": "Advanced ML Service Running",
        "modules": {
            "Context_Aware": True,
            "Location_Aware": True,
            "Crowd_Adaptive": True,
            "Behavior_Intelligent": True,
            "Occlusion_Aware": False,
            "Threat_Aware": True
        },
        "current_context": {
            "location_type": "PUBLIC_OPEN_CROWDED" if not camera else "ACTIVE_MONITORING",
            "active_risk_profile": "High Sensitivity"
        }
    }
    
    # Try to get real context if tracker loops
    # (Since tracker is local... we'd need to expose it globally or read config)
    # For proof of concept, returning the static accepted config is fine.
    
    return jsonify(logic_status)

@app.get("/stats")
def stats():
    """
    Returns real-time statistics from the tracker for the frontend dashboard.
    """
    global tracker_instance
    if tracker_instance:
        return jsonify({
            "status": "active",
            "location_type": tracker_instance.location_context.location_type,
            "crowd_density": tracker_instance.crowd_analyzer.current_density,
            "active_objects": len(tracker_instance.objects),
            "high_risk_count": sum(1 for o in tracker_instance.objects if o.threat_level == "HIGH_RISK" or o.abandonment_confidence > 0.8),
            "modules": {
                "Context_Aware": True,
                "Location_Aware": True,
                "Crowd_Adaptive": True,
                "Behavior_Intelligent": True,
                "Occlusion_Aware": False,
                "Threat_Aware": True
            }
        })
    else:
        return jsonify({
            "status": "initializing",
            "location_type": "Unknown",
            "crowd_density": 0,
            "active_objects": 0,
            "high_risk_count": 0,
            "modules": {}
        })

@app.post("/set_location")
def set_location():
    """
    Updates the location context of the tracker.
    Expects JSON: { "location_type": "PUBLIC_OPEN_CROWDED" }
    """
    global tracker_instance
    if not tracker_instance:
         return jsonify({"status": "error", "message": "Tracker not initialized"}), 503
    
    data = request.json
    new_location = data.get("location_type")
    
    if not new_location:
        return jsonify({"status": "error", "message": "location_type is required"}), 400
        
    # Valid types (could also dynamic load from risk_profile.json keys if we wanted to be fancy)
    valid_types = ["PUBLIC_OPEN_CROWDED", "PUBLIC_REMOTE_AREA", "SEMI_RESTRICTED_ZONE"]
    
    if new_location not in valid_types:
         return jsonify({"status": "error", "message": f"Invalid location type. Valid options: {valid_types}"}), 400
         
    # Update the tracker
    tracker_instance.location_context.set_location_type(new_location)
    
    return jsonify({
        "status": "success", 
        "message": f"Location context updated to {new_location}",
        "current_location": tracker_instance.location_context.location_type
    })

@app.get("/objects")
def get_objects():
    """
    Returns list of currently tracked objects with their details including idle time.
    """
    global tracker_instance
    if tracker_instance and tracker_instance.objects:
        objects_list = []
        
        for obj in tracker_instance.objects:
            if obj.state != "LOST":  # Only return active objects
                objects_list.append({
                    "object_id": obj.id,
                    "class_name": obj.class_name,
                    "state": obj.state,
                    "threat_level": obj.threat_level,
                    "stationary_time": round(obj.stationary_time, 1),
                    "owner_absence_time": round(obj.owner_absence_time, 1),
                    "distance": round(obj.owner_distance, 1) if obj.owner_distance != float('inf') else None,
                    "location_type": tracker_instance.location_context.location_type if tracker_instance.location_context else "UNKNOWN",
                    "crowd_density": tracker_instance.crowd_analyzer.current_density if tracker_instance.crowd_analyzer else 0,
                    "abandonment_score": round(obj.abandonment_confidence, 2),
                    "threshold": getattr(obj, "score_details", {}).get("threshold", 0.8) if hasattr(obj, "score_details") and obj.score_details else 0.8,
                    "alert": getattr(obj, "score_details", {}).get("alert", False) if hasattr(obj, "score_details") and obj.score_details else False,
                    # Fallback / frontend keys
                    "confidence": round(obj.abandonment_confidence, 2),
                    "idle_time": round(obj.stationary_time, 1),  # Legacy fallback
                    "owner_id": obj.owner_id,  # Owner person ID
                    "owner_distance": round(obj.owner_distance, 1) if obj.owner_distance != float('inf') else None,
                    "bbox": obj.bbox,
                    "score_details": getattr(obj, "score_details", None)
                })
        
        return jsonify({
            "status": "success",
            "count": len(objects_list),
            "objects": objects_list
        })
    else:
        return jsonify({
            "status": "success",
            "count": 0,
            "objects": []
        })

@app.get("/db_alerts")
def get_db_alerts():
    """
    Returns recent alerts from the database.
    """
    session = get_db_session()
    if not session:
        return jsonify({"status": "error", "message": "Database not strictly configured or accessible"}), 503
    
    try:
        from sqlalchemy import desc
        alerts = session.query(ObjectAlert).order_by(desc(ObjectAlert.timestamp)).limit(50).all()
        results = []
        for a in alerts:
            results.append({
                "id": a.id,
                "object_id": a.object_id,
                "class_name": a.class_name,
                "state": a.state,
                "threat_level": a.threat_level,
                "confidence": a.confidence,
                "stationary_time": a.stationary_time,
                "location_type": a.location_type,
                "crowd_density": a.crowd_density,
                "owner_id": a.owner_id,
                "object_image_base64": a.object_image_base64,
                "person_image_base64": a.person_image_base64,
                "timestamp": a.timestamp.isoformat()
            })
        session.close()
        return jsonify({"status": "success", "alerts": results})
    except Exception as e:
        session.close()
        return jsonify({"status": "error", "message": str(e)}), 500



# ─── Video Recording Endpoints ────────────────────────────────────────────────

def _recording_worker(filepath, target_fps=50):
    """Background thread that writes annotated frames to a WebM file with exact timestamps."""
    global recording_state, tracker_instance, latest_processed_frame

    # Initial target dimensions
    width, height = 640, 480
    
    # Wait briefly for the first processed frame to grab the right dimensions
    for _ in range(50):
        if latest_processed_frame is not None:
            width = latest_processed_frame.shape[1]
            height = latest_processed_frame.shape[0]
            break
        time.sleep(0.1)

    fourcc = cv2.VideoWriter_fourcc(*'VP80')
    writer = cv2.VideoWriter(filepath, fourcc, float(target_fps), (width, height))

    with recording_lock:
        recording_state["writer"] = writer

    start_time = time.time()
    frames_written = 0
    frame_interval = 1.0 / target_fps

    try:
        while True:
            with recording_lock:
                if not recording_state["active"]:
                    break

            now = time.time()
            expected_frames = int((now - start_time) / frame_interval)
            
            # If we need to write a frame to keep up with chronological time
            if frames_written < expected_frames:
                if latest_processed_frame is not None:
                    frame = latest_processed_frame.copy()
                else:
                    import numpy as np
                    frame = np.zeros((height, width, 3), dtype=np.uint8)

                # Overlay "REC" indicator on recorded frame
                cv2.circle(frame, (width - 30, 25), 10, (0, 0, 255), -1)
                cv2.putText(frame, "REC", (width - 80, 32),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Write frames catching up to real-time sync
                while frames_written < expected_frames:
                    with recording_lock:
                        if not recording_state["active"]:
                            break
                    writer.write(frame)
                    frames_written += 1
            else:
                # Sleep briefly until next frame is due 
                time.sleep(0.01)

    finally:
        writer.release()
        print(f"[RECORDING] Saved: {filepath} ({frames_written} frames)")


@app.post("/start_recording")
def start_recording():
    global recording_state
    with recording_lock:
        if recording_state["active"]:
            return jsonify({"status": "error", "message": "Already recording"}), 400

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename  = f"recording_{timestamp}.webm"
        filepath  = os.path.join(RECORDINGS_DIR, filename)

        recording_state["active"]     = True
        recording_state["filename"]   = filename
        recording_state["start_time"] = time.time()
        recording_state["writer"]     = None

    t = threading.Thread(target=_recording_worker, args=(filepath,), daemon=True)
    with recording_lock:
        recording_state["thread"] = t
    t.start()

    return jsonify({"status": "success", "message": "Recording started", "filename": filename})


@app.post("/stop_recording")
def stop_recording():
    global recording_state
    with recording_lock:
        if not recording_state["active"]:
            return jsonify({"status": "error", "message": "Not recording"}), 400

        filename               = recording_state["filename"]
        recording_state["active"] = False   # signals thread to exit

    return jsonify({"status": "success", "message": "Recording stopped", "filename": filename})


@app.get("/recording_status")
def recording_status():
    with recording_lock:
        active     = recording_state["active"]
        filename   = recording_state["filename"]
        start_time = recording_state["start_time"]

    elapsed = round(time.time() - start_time, 1) if (active and start_time) else 0
    return jsonify({
        "active":   active,
        "filename": filename,
        "elapsed":  elapsed
    })


@app.get("/recordings")
def list_recordings():
    try:
        files = []
        for f in sorted(os.listdir(RECORDINGS_DIR), reverse=True):
            if f.endswith(".webm"):
                fpath = os.path.join(RECORDINGS_DIR, f)
                size  = os.path.getsize(fpath)
                mtime = os.path.getmtime(fpath)
                files.append({
                    "filename": f,
                    "size_mb":  round(size / (1024 * 1024), 2),
                    "recorded_at": datetime.datetime.fromtimestamp(mtime).isoformat()
                })
        return jsonify({"status": "success", "recordings": files})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.get("/recordings/<path:filename>")
def serve_recording(filename):
    return send_from_directory(RECORDINGS_DIR, filename)

@app.delete("/recordings/<path:filename>")
def delete_recording(filename):
    try:
        fpath = os.path.join(RECORDINGS_DIR, filename)
        if os.path.exists(fpath):
            os.remove(fpath)
            return jsonify({"status": "success", "message": f"Deleted {filename}"})
        else:
            return jsonify({"status": "error", "message": "File not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)

