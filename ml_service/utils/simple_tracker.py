import math
import time
import uuid

class TrackedObject:
    def __init__(self, bbox, class_name):
        self.id = str(uuid.uuid4())[:8]
        self.class_name = class_name
        self.bbox = bbox
        self.first_seen = time.time()
        self.last_seen = time.time()
        self.last_position = self.center(bbox)
        self.stationary_time = 0

    def center(self, bbox):
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) // 2, (y1 + y2) // 2)

    def update(self, bbox):
        new_center = self.center(bbox)
        dist = math.dist(self.last_position, new_center)

        if dist < 15:  # pixels
            self.stationary_time += time.time() - self.last_seen
        else:
            self.stationary_time = 0

        self.last_position = new_center
        self.bbox = bbox
        self.last_seen = time.time()
