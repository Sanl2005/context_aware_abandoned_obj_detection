class ScoringEngine:
    def __init__(self, location_context):
        self.location_context = location_context

    def calculate_abandonment_confidence(self, 
                                         stationary_duration, 
                                         owner_absence_time, 
                                         owner_distance, 
                                         threat_level, 
                                         crowd_density_count):
        """
        Computes the final Abandonment Confidence Score based on required weighted factors.
        Returns: (final_score, details_dict)
        """
        weights = self.location_context.current_profile
        
        # 1. Stationary Factor
        # Normalized based on location tolerance
        time_threshold = weights.get("stationary_time_threshold", 60)
        # Non-linear ramp-up: faster escalation after threshold
        stationary_score = min(stationary_duration / time_threshold, 1.0)
        
        # 2. Owner Absence Factor
        # Grace period logic is partially handled in tracker, but we enforce it here too
        # 5s grace, 10s ramp to full
        if owner_absence_time < 5.0:
            absence_score = 0.0
        else:
            absence_score = min((owner_absence_time - 5.0) / 10.0, 1.0)
            
        # 3. Owner-Object Distance Factor (Spatial)
        # Standardize max distance (e.g. 10 meters = 1.0)
        if owner_distance == float('inf'):
            distance_pure_score = 1.0
        else:
            distance_pure_score = min(owner_distance / 10.0, 1.0)
            
        # 6. Crowd Density Adjustment (Must dynamically adjust importance of distance)
        # High density -> Reduce reliance on distance
        crowd_threshold = weights.get("crowd_density_threshold", 10)
        crowd_factor = min(crowd_density_count / crowd_threshold, 1.0)
        
        # Distance weight decreases as crowd increases
        w_dist_base = weights.get("distance_weight", 0.3)
        w_dist_adjusted = w_dist_base * (1.0 - (crowd_factor * 0.8)) # Up to 80% reduction
        
        # 4. Object Threat Type Factor
        # Define base threat scores
        threat_scores = {
            "HIGH_RISK": 1.0,
            "MEDIUM_RISK": 0.6,
            "LOW_RISK": 0.0, # Person/Ignore
            "UNKNOWN": 0.3
        }
        threat_score = threat_scores.get(threat_level, 0.3)
        if threat_level == "LOW_RISK": # Person/Ignore
            details = {
                "threat_level": threat_level,
                "stationary_time": round(stationary_duration, 1),
                "owner_absence_time": round(owner_absence_time, 1),
                "distance": round(owner_distance, 1) if owner_distance != float('inf') else "inf",
                "location_type": self.location_context.location_type,
                "crowd_density": crowd_density_count,
                "abandonment_score": 0.0,
                "threshold": weights.get("alert_threshold", 0.8),
                "alert": False,
                "factors": {
                    "stationary_score": 0.0,
                    "absence_score": 0.0,
                    "distance_score": 0.0,
                    "crowd_adjustment": 0.0
                }
            }
            return 0.0, details

        # 5. Location Type (Implicit via weights)
        w_stat = weights.get("stationary_duration_weight", 0.4)
        w_absence = 0.5 # Hardcoded base importance for absence
        
        # Scored Components
        score_stationary = (stationary_score * w_stat)
        score_absence = (absence_score * w_absence)
        score_distance = (distance_pure_score * w_dist_adjusted)
        
        # Base linear combination
        base_score = score_stationary + score_absence + score_distance
        
        # Threat Level as a Multiplier/Escalator
        # Higher threat level objects should trigger faster
        # If threat is high, boost score by 20%
        if threat_level == "HIGH_RISK":
            base_score *= 1.2
        
        # Final Clamp
        final_score = min(max(base_score, 0.0), 1.0)
        
        # Details for validation
        details = {
            "threat_level": threat_level,
            "stationary_time": round(stationary_duration, 1),
            "owner_absence_time": round(owner_absence_time, 1),
            "distance": round(owner_distance, 1) if owner_distance != float('inf') else "inf",
            "location_type": self.location_context.location_type,
            "crowd_density": crowd_density_count,
            "abandonment_score": round(final_score, 3),
            "threshold": weights.get("alert_threshold", 0.8),
            "alert": final_score > weights.get("alert_threshold", 0.8),
            "factors": {
                "stationary_score": round(stationary_score, 2),
                "absence_score": round(absence_score, 2),
                "distance_score": round(distance_pure_score, 2),
                "crowd_adjustment": round(crowd_factor, 2)
            }
        }
        
        return final_score, details

    def should_alert(self, confidence):
        threshold = self.location_context.get_threshold("alert_threshold", 0.8)
        return confidence > threshold
