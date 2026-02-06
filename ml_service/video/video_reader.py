import cv2
import time

class VideoReader:
    def __init__(self, source=0, target_fps=2):
        """
        source:
          0 -> webcam
          "video.mp4" -> video file
        """
        self.cap = cv2.VideoCapture(source)
        self.target_fps = target_fps
        self.prev_time = 0

        if not self.cap.isOpened():
            raise RuntimeError("❌ Cannot open video source")

    def read_frame(self):
        current_time = time.time()
        if current_time - self.prev_time < 1 / self.target_fps:
            return True, None

        ret, frame = self.cap.read()
        if not ret:
            return False, None

        if frame is not None:
            print("[DEBUG] Frame shape:", frame.shape)

        self.prev_time = current_time
        return True, frame

    def release(self):
        self.cap.release()
