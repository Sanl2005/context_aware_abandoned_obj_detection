import cv2
import numpy as np

class ZoneManager:
    def __init__(self):
        # Placeholder: In a real system, these would be loaded from config
        self.zones = {
            "ENTRY_EXIT": [], # List of polygon points
            "WAITING_AREA": [],
            "RESTRICTED": []
        }
    
    def set_zones(self, zone_config):
        """
        zone_config: dict of zone_name -> list of points [[x,y], ...]
        """
        self.zones = zone_config

    def get_zone_risk(self, bbox):
        """
        Returns a risk multiplier based on which zone the bbox center falls into.
        """
        cx = (bbox[0] + bbox[2]) / 2
        cy = (bbox[1] + bbox[3]) / 2
        point = (cx, cy)
        
        for name, poly_points in self.zones.items():
            if not poly_points:
                continue
                
            # Check if point in polygon
            # Convert points to appropriate format for cv2.pointPolygonTest
            pts = np.array(poly_points, np.int32)
            pts = pts.reshape((-1, 1, 2))
            
            dist = cv2.pointPolygonTest(pts, point, False)
            if dist >= 0:
                if name == "RESTRICTED":
                    return 2.0
                elif name == "ENTRY_EXIT":
                    return 1.5
                elif name == "WAITING_AREA":
                    return 1.2
                    
        return 1.0 # Default risk
