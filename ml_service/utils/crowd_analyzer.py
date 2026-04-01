class CrowdAnalyzer:
    def __init__(self):
        self.current_density = 0
    
    def update_density(self, detections):
        """
        Updates crowd density based on number of people detected.
        """
        person_count = sum(1 for d in detections if d['class_name'] == 'person')
        self.current_density = person_count
        return self.current_density

    def get_crowd_factor(self, threshold=10):
        """
        Returns a factor (0.0 to 1.0) representing crowd intensity relative to a threshold.
        """
        if self.current_density == 0:
            return 0.0
        
        factor = self.current_density / threshold
        return min(factor, 1.0)
