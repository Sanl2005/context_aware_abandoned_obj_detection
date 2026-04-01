import time

class OcclusionHandler:
    def __init__(self, state_manager):
        self.state_manager = state_manager
        
    def handle_occlusion(self, object_id, last_known_bbox):
        """
        Called when an object is lost from tracking but not confirmed removed.
        """
        # Check current state
        state_data = self.state_manager.get_object_state(object_id)
        if not state_data:
            return

        current_state = state_data.get("state", "VISIBLE")
        
        if current_state == "VISIBLE":
            print(f"[INFO] Object {object_id} possibly occluded. Transitioning state.")
            self.state_manager.update_object_state(object_id, {
                "state": "OCCLUDED",
                "occlusion_start": time.time(),
                "last_confidence": state_data.get("confidence", 0)
            })
            
    def handle_reappearance(self, object_id, current_bbox):
        """
        Called when an object matches an existing tracked ID.
        """
        state_data = self.state_manager.get_object_state(object_id)
        if state_data and state_data.get("state") == "OCCLUDED":
             print(f"[INFO] Object {object_id} reappeared.")
             self.state_manager.update_object_state(object_id, {
                "state": "VISIBLE",
                "occlusion_start": None,
                "last_position": current_bbox
            })

    def check_occlusion_timeout(self, object_id, max_duration=300):
        """
        check if occlusion has lasted too long (assumed removed or lost).
        Returns True if should be removed.
        """
        state_data = self.state_manager.get_object_state(object_id)
        if state_data.get("state") == "OCCLUDED":
            start_time = float(state_data.get("occlusion_start", 0))
            if time.time() - start_time > max_duration:
                return True
        return False
