from .simple_tracker import TrackedObject
from .redis_state_manager import RedisStateManager
from .location_context import LocationContext
from .scoring_engine import ScoringEngine
from .threat_classifier import ThreatClassifier
from .behavior_analyzer import BehaviorAnalyzer
from .crowd_analyzer import CrowdAnalyzer
from .zone_manager import ZoneManager
from .ownership_tracker import OwnershipTracker
import time

class ObjectTracker:
    def __init__(self, location_type="PUBLIC_OPEN_CROWDED"):
        self.objects = []
        
        # Initialize Managers
        self.redis_manager = RedisStateManager()
        self.location_context = LocationContext(location_type)
        self.scoring_engine = ScoringEngine(self.location_context)
        self.threat_classifier = ThreatClassifier()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.crowd_analyzer = CrowdAnalyzer()
        self.zone_manager = ZoneManager() # Defaults for now
        self.ownership_tracker = OwnershipTracker()

    def update(self, detections, pose_detections=None):
        """
        Main update loop for tracking objects.
        """
        # Filter only the classes we want to track
        ALLOWED_CLASSES = [
            "person", "handbag", "backpack", "suitcase",
            "cell phone", 
            "laptop", "bottle","water bottle"
        ]
        
        # Pre-filter detections to only include allowed classes
        detections = [d for d in detections if d.get("class_name") in ALLOWED_CLASSES]
        
        # Update Crowd Density (only with allowed classes)
        self.crowd_analyzer.update_density(detections)
        
        current_time = time.time()
        
        # Filter relevant objects
        relevant_detections = []
        for det in detections:
            # Check threat level
            threat_level, threat_score = self.threat_classifier.classify_threat(det["class_name"])
            det["threat_level"] = threat_level
            det["threat_score"] = threat_score
            
            # Track all objects for visualization, even if unknown threat
            relevant_detections.append(det)

        # Simple IoU Tracking (Association)
        # In a real system, use DeepSORT or stronger tracker
        unmatched_detections = relevant_detections[:]
        
        for obj in self.objects:
            matched = False
            best_iou = 0
            best_det = None
            
            for det in unmatched_detections:
                iou = self._iou(obj.bbox, det["bbox"])
                if iou > 0.4 and iou > best_iou:
                    best_iou = iou
                    best_det = det
            
            if best_det:
                # Update tracks
                prev_bbox = obj.bbox
                obj.update(best_det["bbox"]) # This updates last_seen time too
                
                # Compute velocity (pixels/sec) roughly
                time_diff = current_time - (obj.last_seen - 0.033) # approximate frame time if update happens every frame
                # Better: use obj.last_seen updated inside obj.update vs previous obj.last_seen
                # Let's trust behavior_analyzer to handle history, pass raw movement per frame for now
                movement = ((obj.bbox[0]-prev_bbox[0])**2 + (obj.bbox[1]-prev_bbox[1])**2)**0.5
                velocity = movement # Pixels per frame approx
                
                obj.class_name = best_det["class_name"] # Update class if changed (refinement)
                if obj.class_name == "person":
                    obj.owner_id = None
                    
                    # --- POSE & BEHAVIOR ANALYSIS ---
                    keypoints = None
                    if pose_detections:
                        # Find matching pose
                        best_kp = None
                        min_dist_kp = float('inf')
                        ox, oy = (obj.bbox[0]+obj.bbox[2])/2, (obj.bbox[1]+obj.bbox[3])/2
                        
                        for pd in pose_detections:
                            pb = pd['bbox']
                            px, py = (pb[0]+pb[2])/2, (pb[1]+pb[3])/2
                            dist_kp = ((ox-px)**2 + (oy-py)**2)**0.5
                            
                            if dist_kp < 50: # Threshold for matching pose to detection
                                if dist_kp < min_dist_kp:
                                    min_dist_kp = dist_kp
                                    best_kp = pd['keypoints']
                        
                        keypoints = best_kp

                    # Update behavior state
                    behavior_stats = self.behavior_analyzer.update_owner_state(obj.id, obj.bbox, velocity, keypoints)
                    
                    obj.is_running = behavior_stats.get("is_running", False)
                    obj.is_loitering = behavior_stats.get("nervous_loitering", False)
                    # --------------------------------

                unmatched_detections.remove(best_det)
                matched = True
                
                # Calculate scores
                # Use actual stationary_time from TrackedObject, NOT age (current - first_seen)
                # This prevents moving objects from being marked abandoned.
                stationary_duration = obj.stationary_time

                # --- PREVIOUSLY INLINE LOGIC REMOVED ---
                # All factor evaluation is now delegated to ScoringEngine
                # to ensure strict adherence to the requested factor list.
                
                # Use centralized scoring engine with STRICT factor inputs
                confidence, score_details = self.scoring_engine.calculate_abandonment_confidence(
                    stationary_duration=stationary_duration,
                    owner_absence_time=obj.owner_absence_time,
                    owner_distance=obj.owner_distance,
                    threat_level=best_det["threat_level"],
                    crowd_density_count=self.crowd_analyzer.current_density
                )
                
                # Attach details to object for specialized display/logging if needed
                obj.score_details = score_details
                
                # FINAL OVERRIDE: If owner is definitively nearby/wearing, confidence = 0
                # Using distance check from earlier logic or ensure scoring engine handles it.
                # Scoring engine handles owner_distance < 2.0 -> 0.0 score, but let's be double safe for carry logic
                if obj.owner_id and obj.owner_distance < 1.0:
                    confidence = 0.0

                obj.abandonment_confidence = confidence
                

                obj.threat_level = best_det["threat_level"]
                
                # Update Redis
                self.redis_manager.update_object_state(obj.id, {
                    "bbox": obj.bbox,
                    "confidence": confidence,
                    "last_seen": current_time,
                    "threat_level": obj.threat_level,
                    "score_details": score_details
                })
                
            else:
                # Lost Object -> Mark as lost (will be cleaned up)
                obj.state = "LOST"

        # Add new objects
        for det in unmatched_detections:
            # Try Re-Identification first
            reid_obj = self._attempt_reid(det)
            if reid_obj:
                # Found a match from lost objects!
                reid_obj.update(det["bbox"])
                reid_obj.state = "VISIBLE"
                self.objects.append(reid_obj)
                continue

            new_obj = TrackedObject(det["bbox"], det["class_name"])
            new_obj.threat_level = det["threat_level"]
            
            # --- OWNER ASSIGNMENT ---
            # If this is an item (not a person), try to find a person nearby to assign as owner
            if det["class_name"] != "person":
                min_dist = float('inf')
                best_owner = None
                
                # Look at existing objects that are people
                for existing_obj in self.objects:
                    if existing_obj.class_name == "person" and existing_obj.state == "VISIBLE":
                        # 1. Distance Check
                        center_new = new_obj.last_position
                        center_existing = existing_obj.last_position
                        dist = ((center_new[0]-center_existing[0])**2 + (center_new[1]-center_existing[1])**2)**0.5
                        
                        # 2. Overlap/Intersection Check (More robust than Containment)
                        iou = self._iou(new_obj.bbox, existing_obj.bbox)
                        
                        # If meaningful overlap (item is ON the person)
                        if iou > 0.05: # Even 5% overlap is significant for carried items
                             best_owner = existing_obj
                             min_dist = 0 # Priority
                             break 
                        
                        # 3. Containment Check (Backup)
                        ex1, ey1, ex2, ey2 = existing_obj.bbox
                        nx, ny = center_new
                        is_inside = (ex1 < nx < ex2) and (ey1 < ny < ey2)

                        if is_inside:
                            best_owner = existing_obj
                            min_dist = 0
                            break
                        
                        # 4. Proximity Check
                        if dist < 200.0 and dist < min_dist: 
                            min_dist = dist
                            best_owner = existing_obj
                
                if best_owner:
                    new_obj.owner_id = best_owner.id
            # ------------------------

            self.objects.append(new_obj)
            
            # Init Redis
            self.redis_manager.update_object_state(new_obj.id, {
                "bbox": det["bbox"],
                "class_name": det["class_name"],
                "first_seen": current_time,
                "state": "VISIBLE",
                "threat_level": det["threat_level"]
            })

        # Update ownership tracking (assign owners based on proximity to persons)
        persons = [o for o in self.objects if o.class_name == 'person']
        non_person_objects = [o for o in self.objects if o.class_name != 'person']
        self.ownership_tracker.update_ownership(persons, non_person_objects)
        
        # Cleanup lost objects (remove objects that are no longer being tracked)
        self.objects = [o for o in self.objects if o.state != "LOST"]

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

    def _attempt_reid(self, det):
        """
        Try to match a new detection with a recently lost/occluded object.
        Simple spatial ReID: Class match + Location proximity.
        """
        # Get list of tracked objects that are currently NOT in self.objects (which is active ones)
        # However, self.objects contains ALL tracked objects in this simple implementation, 
        # including those occluded but not timed out.
        # So we look for objects in self.objects that have state="OCCLUDED"
        
        best_match = None
        min_dist = float('inf')
        
        det_center = ((det["bbox"][0]+det["bbox"][2])/2, (det["bbox"][1]+det["bbox"][3])/2)
        
        for obj in self.objects:
            if obj.state == "OCCLUDED" and obj.class_name == det["class_name"]:
                # Check distance from last known position
                last_center = obj.last_position
                dist = ((det_center[0]-last_center[0])**2 + (det_center[1]-last_center[1])**2)**0.5
                
                # Threshold for ReID (e.g., 100 pixels) - larger than frame-to-frame matching
                if dist < 150.0 and dist < min_dist:
                    min_dist = dist
                    best_match = obj
                    
        return best_match
