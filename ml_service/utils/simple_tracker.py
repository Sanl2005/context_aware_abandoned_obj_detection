import math
import time
import uuid

class TrackedObject:
    def __init__(self, bbox, class_name):
        self.id = str(uuid.uuid4())[:8]
        self.class_name = class_name
        self.bbox = bbox
        self.last_bbox = bbox
        
        self.first_seen = time.time()
        self.last_seen = time.time()
        self.last_position = self.center(bbox)
        
        self.stationary_time = 0.0
        
        # New Attributes
        self.threat_level = "UNKNOWN"
        self.abandonment_confidence = 0.0
        self.state = "VISIBLE" # VISIBLE, OCCLUDED, CONFIRMED_REMOVED
        self.owner_id = None # ID of the person associated with this object
        self.owner_assigned_at = None  # Timestamp when owner was assigned
        self.owner_distance = float('inf')  # Current distance to owner in meters
        self.owner_absence_time = 0.0 # Time in seconds the owner has been away

    def center(self, bbox):
        x1, y1, x2, y2 = bbox
        return ((x1 + x2) / 2, (y1 + y2) / 2)

    def update(self, bbox):
        current_time = time.time()
        time_elapsed = current_time - self.last_seen
        
        new_center = self.center(bbox)
        dist = math.dist(self.last_position, new_center)

        if dist < 15:  # pixels threshold for stationary
            self.stationary_time += time_elapsed
        else:
            # If moved significantly, reset stationary timer?
            # Or reduce it? lets reset for strict stationary requirement
            self.stationary_time = 0.0

        self.last_position = new_center
        self.last_bbox = self.bbox
        self.bbox = bbox
        self.last_seen = current_time
