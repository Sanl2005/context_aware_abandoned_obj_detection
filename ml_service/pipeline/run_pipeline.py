import cv2

from ml_service.video.video_reader import VideoReader
from ml_service.models.yolo_detector import YOLODetector
from ml_service.utils.object_tracker import ObjectTracker


def main():
    video = VideoReader(source=0)  # 0 for webcam or path to video file
    detector = YOLODetector()

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

        # ✅ Update tracker with detections
        tracked_objects = tracker.update(detections)

        # Draw detections
        for d in detections:
            print(f"[DEBUG] Detected: {d['class_name']} ({d['confidence']:.2f})")

            if d["class_name"] in [
                "person", "handbag", "backpack", "suitcase",
                "cell phone", "teddy bear", "chair",
                "tv", "remote", "keyboard", "mouse", "book",
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

        cv2.imshow("YOLOv8 Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    video.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
