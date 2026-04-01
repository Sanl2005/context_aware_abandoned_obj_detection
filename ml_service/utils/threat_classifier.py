class ThreatClassifier:
    def __init__(self):
        # Only track the specified 9 classes
        self.threat_categories = {
            "HIGH_RISK": ["suitcase", "backpack"],
            "MEDIUM_RISK": ["handbag", "bottle"],
            "LOW_RISK": ["person", "cell phone", "laptop"]
        }

    def classify_threat(self, object_class_name):
        """
        Returns the threat level (string) and a numeric score for the object class.
        """
        class_lower = object_class_name.lower()
        
        if class_lower == "person":
             return "LOW_RISK", 0.1 # Ignore people for abandonment
        elif class_lower in self.threat_categories["HIGH_RISK"]:
            return "HIGH_RISK", 1.0
        elif class_lower in self.threat_categories["MEDIUM_RISK"] or class_lower in self.threat_categories["LOW_RISK"]:
            return "MEDIUM_RISK", 0.4 # Monitor these items
        else:
            return "UNKNOWN", 0.3
            
    def get_threat_categories(self):
        return self.threat_categories
