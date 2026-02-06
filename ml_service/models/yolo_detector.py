import torch

# Monkeypatch torch.load to fix 'weights_only' issue with Ultralytics on Torch 2.6+
_original_load = torch.load
def safe_load(*args, **kwargs):
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_load(*args, **kwargs)
torch.load = safe_load

from ultralytics import YOLO
try:
    from ultralytics.nn.tasks import DetectionModel
    torch.serialization.add_safe_globals([DetectionModel])
except ImportError:
    pass

class YOLODetector:
    def __init__(self, model_path="yolov8n.pt"):
        print("[INFO] Loading YOLO model...")
        self.model = YOLO(model_path)
        print("[INFO] YOLO model loaded successfully")

    def detect(self, frame):
        print("[DEBUG] Running YOLO inference on frame")

        results = self.model(
            frame,
            conf=0.25,      # LOWER confidence threshold
            verbose=False
        )

        detections = []

        for r in results:
            if r.boxes is None:
                print("[DEBUG] No boxes detected in this frame")
                continue

            for box in r.boxes:
                cls_id = int(box.cls[0])
                confidence = float(box.conf[0])
                x1, y1, x2, y2 = map(float, box.xyxy[0])

                detections.append({
                    "class_id": cls_id,
                    "class_name": self.model.names[cls_id],
                    "confidence": confidence,
                    "bbox": [x1, y1, x2, y2]
                })

        print(f"[DEBUG] Total detections: {len(detections)}")
        return detections
