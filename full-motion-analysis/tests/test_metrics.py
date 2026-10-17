import unittest

import numpy as np

from motionlab.metrics import histogram_distance, measure_frame_pair, robust_high_threshold


class MetricTests(unittest.TestCase):
    def test_static_pair_has_no_difference(self):
        frame = np.zeros((64, 64), dtype=np.uint8)
        result = measure_frame_pair(frame, frame.copy())
        self.assertEqual(result["mean_abs_diff"], 0.0)
        self.assertEqual(result["changed_pixel_ratio"], 0.0)
        self.assertIsNone(result["flow_mean_magnitude_px_frame"])

    def test_motion_is_measured_even_when_histogram_is_unchanged(self):
        before = np.zeros((64, 64), dtype=np.uint8)
        after = before.copy()
        before[20:30, 10:20] = 220
        after[20:30, 12:22] = 220
        result = measure_frame_pair(before, after)
        self.assertGreater(result["mean_abs_diff"], 0.0)
        self.assertGreater(result["changed_pixel_ratio"], 0.0)
        self.assertAlmostEqual(histogram_distance(before, after), 0.0)

    def test_invalid_frames_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "frame_shapes_must_match"):
            measure_frame_pair(np.zeros((64, 64), dtype=np.uint8), np.zeros((65, 64), dtype=np.uint8))
        with self.assertRaisesRegex(ValueError, "frames_must_be_2d_grayscale"):
            measure_frame_pair(np.zeros((64, 64, 3), dtype=np.uint8), np.zeros((64, 64, 3), dtype=np.uint8))

    def test_robust_threshold_is_deterministic_and_floored(self):
        values = [0.01, 0.01, 0.01, 0.01, 0.9]
        self.assertEqual(robust_high_threshold(values, floor=0.02), robust_high_threshold(values, floor=0.02))
        self.assertGreaterEqual(robust_high_threshold(values, floor=0.02), 0.02)


if __name__ == "__main__":
    unittest.main()
