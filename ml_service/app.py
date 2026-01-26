from flask import Flask, request, jsonify
from ultralytics import YOLO
import requests
import datetime
import os

app = Flask(__name__)

# Load YOLO model (small + fast)
model = YOLO("yolov8n.pt")

RAILS_API = "http://127.0.0.1:3000/api/detected_objects"


@app.get("/status")
def status():
    return jsonify({"status": "ok", "message": "Flask ML Service running"})


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
