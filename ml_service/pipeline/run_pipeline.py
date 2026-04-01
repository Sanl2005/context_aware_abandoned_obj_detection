import cv2

import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from ml_service.video.video_reader import VideoReader
from ml_service.models.yolo_detector import YOLODetector
from ml_service.utils.object_tracker import ObjectTracker
from ultralytics import YOLO

def main():
    video = VideoReader(source=0)  # 0 for webcam or path to video file
    detector = YOLODetector()
    
    print("Loading Pose Model...")
    try:
        pose_model = YOLO('yolov8n-pose.pt')
    except Exception as e:
        print(f"Warning: Could not load Pose Model: {e}")
        pose_model = None

    # ✅ Initialize tracker before loop
    tracker = ObjectTracker()

    while True:
        active, frame = video.read_frame()
        if not active:
            break

        if frame is None:
            cv2.waitKey(10)
            continue

        # YOLO detection
        detections = detector.detect(frame)

        # Pose Estimation
        pose_detections = []
        if pose_model:
            try:
                pose_results = pose_model(frame, verbose=False)
                if pose_results:
                    r = pose_results[0]
                    if r.boxes and r.keypoints:
                         # Iterate through results
                         boxes = r.boxes.xyxy.cpu().numpy()
                         kpts = r.keypoints.data.cpu().numpy() # (N, 17, 3)
                         
                         for i in range(len(boxes)):
                             pose_detections.append({
                                 'bbox': boxes[i],
                                 'keypoints': kpts[i]
                             })
            except Exception as e:
                print(f"[ERROR] Pose Inference Failed: {e}")

        # ✅ Update tracker with detections AND pose
        tracked_objects = tracker.update(detections, pose_detections)

        # Draw detections
        for d in detections:
            print(f"[DEBUG] Detected: {d['class_name']} ({d['confidence']:.2f})")

            if d["class_name"] in [
                "person", "handbag", "backpack", "suitcase",
                "cell phone", "remote",
                "laptop", "water bottle", "bottle"
            ]:
                x1, y1, x2, y2 = map(int, d["bbox"])
                label = f'{d["class_name"]} {d["confidence"]:.2f}'

                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    frame, label, (x1, y1 - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2
                )

        # ✅ Abandoned object alert logic
        for obj in tracked_objects:
            if obj.stationary_time > 10:
                print(
                    f"[ALERT] Possible abandoned {obj.class_name} | ID={obj.id}"
                )
            
            # Behavior Alerts
            if getattr(obj, "is_running", False):
                print(f"[ALERT] Behavior Detect: Person {obj.id} is RUNNING")
                cv2.putText(frame, "RUNNING", (int(obj.bbox[0]), int(obj.bbox[1]-20)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                           
            if getattr(obj, "is_loitering", False):
                 print(f"[ALERT] Behavior Detect: Person {obj.id} is LOITERING NERVOUSLY")
                 cv2.putText(frame, "NERVOUS", (int(obj.bbox[0]), int(obj.bbox[1]-20)), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 165, 255), 2)

        cv2.imshow("YOLOv8 Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
