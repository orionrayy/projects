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

    def test_dense_flow_returns_spatial_grid_when_backend_is_present(self):
        class FakeCV2:
            RANSAC = 8

            @staticmethod
            def calcOpticalFlowFarneback(previous, current, _flow, *_args):
                flow = np.zeros((*previous.shape, 2), dtype=np.float32)
                flow[16:48, 16:48, 0] = 2.0
                return flow

            @staticmethod
            def estimateAffinePartial2D(source, destination, **_kwargs):
                matrix = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]], dtype=np.float32)
                inliers = np.ones((len(source), 1), dtype=np.uint8)
                return matrix, inliers

        before = np.zeros((64, 64), dtype=np.uint8)
        after = before.copy()
        result = measure_frame_pair(before, after, cv2_module=FakeCV2)
        self.assertEqual(len(result["flow_grid"]), 24)
        self.assertGreater(result["flow_moving_pixel_ratio"], 0)
        cell_ratios = [cell["moving_pixel_ratio"] for cell in result["flow_grid"]]
        self.assertGreater(max(cell_ratios), min(cell_ratios))
        self.assertGreaterEqual(result["flow_magnitude_p90_px_frame"], 0)
        self.assertEqual(result["global_affine_fit_status"], "fit")
        self.assertAlmostEqual(result["global_affine_scale_factor"], 1.0)
        self.assertGreaterEqual(result["global_affine_inlier_ratio"], 0.99)

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
