import unittest
import time
from unittest.mock import MagicMock
from ml_service.utils.occlusion_handler import OcclusionHandler

class TestOcclusionHandler(unittest.TestCase):
    def setUp(self):
        self.mock_redis = MagicMock()
        self.handler = OcclusionHandler(self.mock_redis)

    def test_visible_to_occluded(self):
        # Mock object in VISIBLE state
        self.mock_redis.get_object_state.return_value = {"state": "VISIBLE", "confidence": 0.5}
        
        self.handler.handle_occlusion("obj_123", [10, 10, 50, 50])
        
        # Verify state update called
        self.mock_redis.update_object_state.assert_called()
        args = self.mock_redis.update_object_state.call_args[0]
        self.assertEqual(args[0], "obj_123")
        self.assertEqual(args[1]["state"], "OCCLUDED")
        self.assertIsNotNone(args[1]["occlusion_start"])

    def test_occluded_to_reappeared(self):
        # Mock object in OCCLUDED state
        self.mock_redis.get_object_state.return_value = {
            "state": "OCCLUDED", 
            "occlusion_start": time.time() - 30
        }
        
        self.handler.handle_reappearance("obj_123", [15, 15, 55, 55])
        
        # Verify state update called
        self.mock_redis.update_object_state.assert_called()
        args = self.mock_redis.update_object_state.call_args[0]
        self.assertEqual(args[1]["state"], "VISIBLE")
        self.assertIsNone(args[1]["occlusion_start"])

    def test_occlusion_timeout(self):
        # Mock object occluded for long time
        long_ago = time.time() - 1000
        self.mock_redis.get_object_state.return_value = {
            "state": "OCCLUDED", 
            "occlusion_start": long_ago
        }
        
        is_removed = self.handler.check_occlusion_timeout("obj_123", max_duration=300)
        self.assertTrue(is_removed)

if __name__ == '__main__':
    unittest.main()
