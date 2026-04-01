import json
import os

class LocationContext:
    def __init__(self, location_type="PUBLIC_OPEN_CROWDED", config_path="risk_profile.json"):
        self.location_type = location_type
        self.config = self._load_config(config_path)
        self.current_profile = self.config.get(self.location_type, {})

    def _load_config(self, path):
        if not os.path.exists(path):
            # Fallback default
            return {
                "PUBLIC_OPEN_CROWDED": {
                    "distance_weight": 0.1,
                    "stationary_duration_weight": 0.4,
                    "alert_threshold": 0.85
                }
            }
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to load risk profile: {e}")
            return {}

    def set_location_type(self, location_type):
        if location_type in self.config:
            self.location_type = location_type
            self.current_profile = self.config[location_type]
            print(f"[INFO] Location context switched to: {location_type}")
        else:
            print(f"[WARNING] Unknown location type: {location_type}")

    def get_weight(self, key, default=0.5):
        return self.current_profile.get(key, default)

    def get_threshold(self, key, default=0.8):
        return self.current_profile.get(key, default)
