import math
import numpy as np

class BehaviorAnalyzer:
    def __init__(self):
        self.history = {} # Store history of owner movements: {id: {"actions": [], "keypoints": [], "bbox": []}}
        self.window_size = 30 # Number of frames to keep history

    def update_owner_state(self, owner_id, bbox, velocity, keypoints=None):
        """
        Updates owner state and detects suspicious behavior.
        bbox: [x1, y1, x2, y2]
        velocity: estimated velocity
        keypoints: Array of shape (17, 2) or (17, 3) from YOLO Pose
        """
        if owner_id not in self.history:
            self.history[owner_id] = {"keypoints": [], "bbox": []}

        hist = self.history[owner_id]    
        
        # Append latest data
        hist["bbox"].append(bbox)
        if keypoints is not None:
            hist["keypoints"].append(keypoints)

        # Maintain window size
        if len(hist["bbox"]) > self.window_size:
            hist["bbox"].pop(0)
        if len(hist["keypoints"]) > self.window_size:
            hist["keypoints"].pop(0)

        # Basic velocity check
        is_running_basic = velocity > 5.0 # Arbitrary threshold

        # Advanced Pose Analysis
        pose_analysis = self._analyze_pose_behavior(hist)
        
        return {
            "is_running": pose_analysis.get("running", is_running_basic),
            "nervous_loitering": pose_analysis.get("nervous_loitering", False),
            "suspicious_move": False # Placeholder
        }

    def _analyze_pose_behavior(self, hist):
        """
        Detects specific behaviors based on pose history.
        """
        if len(hist["keypoints"]) < 5:
            return {"running": False, "nervous_loitering": False}

        # 1. RUNNING (High Movement + Posture)
        # Calculate displacement over last few frames
        start_bb = hist["bbox"][0]
        end_bb = hist["bbox"][-1]
        cx1, cy1 = (start_bb[0]+start_bb[2])/2, (start_bb[1]+start_bb[3])/2
        cx2, cy2 = (end_bb[0]+end_bb[2])/2, (end_bb[1]+end_bb[3])/2
        displacement = math.sqrt((cx2-cx1)**2 + (cy2-cy1)**2)
        
        # Check stride length if keypoints available
        latest_kp = hist["keypoints"][-1]
        
        # Keypoints: 15 (Left Ankle), 16 (Right Ankle), 0 (Nose)
        # Ensure we have valid keypoints (not 0,0)
        stride_check = False
        if len(latest_kp) >= 17:
            # Check confidence if available (index 2), usually (x,y) or (x,y,conf)
            # Assuming (x,y) or taking first 2
            la = latest_kp[15][:2]
            ra = latest_kp[16][:2]
            nose = latest_kp[0][:2]
            
            # Simple validity check: are they non-zero?
            if la[0] > 1 and ra[0] > 1 and nose[1] > 1:
                ankle_dist = abs(la[0] - ra[0])
                # Estimate height as ankle_y - nose_y (rough approximation)
                height = max((la[1] + ra[1])/2 - nose[1], 10.0) 
                
                norm_stride = ankle_dist / height
                if norm_stride > 0.4: # Wide stride indicative of running
                    stride_check = True

        is_running = (displacement > 30) and stride_check

        # 2. NERVOUS LOITERING (Low Movement + High Fidgeting)
        is_nervous = False
        if displacement < 20: # Relatively stationary
            # Calculate variance of keypoints (Wrists: 9, 10; Head: 0-4)
            # Stack history to numpy array for easy calculation
            try:
                # Shape: (Frames, 17, 2+)
                kp_hist = np.array([k[:, :2] for k in hist["keypoints"]]) 
                
                # Calculate variance of wrists (indices 9, 10)
                # We want the variance of their position relative to the body center (hip center)
                # to avoid detecting camera shake or whole body sway as fidgeting?
                # For now, just raw variance.
                
                # Wrists (9, 10)
                wrist_movement = np.std(kp_hist[:, [9, 10], :], axis=0).mean()
                
                # If wrist movement is high but body displacement is low -> Nervous/Fidgeting
                if wrist_movement > 5.0: # Threshold needs tuning
                    is_nervous = True
            except Exception:
                pass # NumPy error or empty list

        return {"running": is_running, "nervous_loitering": is_nervous}

    def analyze_separation(self, object_pos, owner_pos):
        """
        Analyzes the separation event.
        Returns a score (0.0 to 1.0) indicating suspicion level.
        """
        # Calculate distance
        ox, oy = (object_pos[0]+object_pos[2])/2, (object_pos[1]+object_pos[3])/2
        px, py = (owner_pos[0]+owner_pos[2])/2, (owner_pos[1]+owner_pos[3])/2
        
        dist = math.sqrt((ox-px)**2 + (oy-py)**2)
        
        # If owner is far away very quickly, high suspicion
        return min(dist / 500.0, 1.0) # Normalizing distance
