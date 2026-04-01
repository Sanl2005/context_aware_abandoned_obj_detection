import unittest
from ml_service.utils.scoring_engine import ScoringEngine
from ml_service.utils.location_context import LocationContext

class TestScoringEngine(unittest.TestCase):
    def setUp(self):
        # Mock LocationContext logic
        self.context = LocationContext("PUBLIC_OPEN_CROWDED")
        self.engine = ScoringEngine(self.context)

    def test_low_risk_scenario(self):
        # Scenario: Short duration, moving owner nearby
        score = self.engine.calculate_abandonment_confidence(
            distance_score=0.1,
            interaction_gap_score=0.1,
            stationary_duration=10, # seconds
            owner_reid_score=0.1,
            zone_risk_score=1.0,
            crowd_density_score=0.5,
            behavior_score=0.0,
            occlusion_score=0.0,
            threat_type_score=0.2 # low risk item
        )
        self.assertLess(score, 0.5, "Score should be low for safe scenario")

    def test_high_risk_abandonment(self):
        # Scenario: Long duration, high threat item, owner far away
        score = self.engine.calculate_abandonment_confidence(
            distance_score=1.0, # Far
            interaction_gap_score=0.8,
            stationary_duration=120, # 2 mins
            owner_reid_score=0.9,
            zone_risk_score=1.2, # Slight risk zone enhancement
            crowd_density_score=0.2, # Low crowd (more suspicious)
            behavior_score=0.8, # Suspicious behavior
            occlusion_score=0.0,
            threat_type_score=1.0 # High risk item
        )
        self.assertGreater(score, 0.8, "Score should be high for clear abandonment")

    def test_crowded_environment_damping(self):
        # Scenario: Crowded place, distance is unreliable
        # We expect the profile to have low weight for distance
        score = self.engine.calculate_abandonment_confidence(
            distance_score=0.8, # "Far" but could be error
            interaction_gap_score=0.2,
            stationary_duration=30, 
            owner_reid_score=0.5,
            zone_risk_score=1.0,
            crowd_density_score=1.0, # Very crowded
            behavior_score=0.1,
            occlusion_score=0.0,
            threat_type_score=0.6 # Medium threat
        )
        # Should not alert yet
        self.assertLess(score, 0.85)

if __name__ == '__main__':
    unittest.main()
