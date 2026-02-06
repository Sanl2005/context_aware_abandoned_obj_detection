from ml_service.utils.simple_tracker import TrackedObject

class ObjectTracker:
    def __init__(self):
        self.objects = []

    def update(self, detections):
        for det in detections:
            if det["class_name"] not in ["backpack", "handbag", "suitcase"]:
                continue

            matched = False
            for obj in self.objects:
                if self._iou(obj.bbox, det["bbox"]) > 0.4:
                    obj.update(det["bbox"])
                    matched = True
                    break

            if not matched:
                self.objects.append(
                    TrackedObject(det["bbox"], det["class_name"])
                )

        return self.objects

    def _iou(self, a, b):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b

        inter_x1 = max(ax1, bx1)
        inter_y1 = max(ay1, by1)
        inter_x2 = min(ax2, bx2)
        inter_y2 = min(ay2, by2)

        inter_area = max(0, inter_x2 - inter_x1) * max(0, inter_y2 - inter_y1)
        area_a = (ax2 - ax1) * (ay2 - ay1)
        area_b = (bx2 - bx1) * (by2 - by1)

        return inter_area / (area_a + area_b - inter_area + 1e-6)
