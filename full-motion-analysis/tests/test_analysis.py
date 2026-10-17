import unittest

from motionlab.analysis import detect_event_candidates


def row(i, dx, dy, magnitude):
    return {
        "frame_index": i,
        "timestamp_s": i / 10.0,
        "mean_abs_diff": 0.02,
        "changed_pixel_ratio": 0.05,
        "histogram_delta": 0.0,
        "mean_luma": 0.2,
        "flow_mean_dx_px_frame": dx,
        "flow_mean_dy_px_frame": dy,
        "flow_mean_magnitude_px_frame": magnitude,
        "flow_global_median_dx_px_frame": dx,
        "flow_global_median_dy_px_frame": dy,
        "flow_residual_mean_px_frame": 0.2,
        "flow_coherence": 0.9,
        "direction_deg_image_coordinates": 0.0,
        "exact_duplicate_of_previous": False,
    }


class TemporalEventTests(unittest.TestCase):
    def test_reversal_is_a_candidate_not_a_causal_claim(self):
        rows = [row(0, 0.0, 0.0, 0.0), row(1, 2.0, 0.0, 2.0), row(2, 2.0, 0.0, 2.0), row(3, -2.0, 0.0, 2.0)]
        events = detect_event_candidates(rows, 10.0)
        reversals = [e for e in events if e["event_type"] == "direction_reversal_candidate"]
        self.assertTrue(reversals)
        self.assertEqual(reversals[0]["rule_id"], "FMA-REVERSAL-001")
        self.assertIn("not proof", reversals[0]["interpretation_limit"])

    def test_scene_cut_requires_large_observed_change(self):
        rows = [row(0, 0.0, 0.0, 0.0), row(1, 0.0, 0.0, 0.0)]
        rows[1]["mean_abs_diff"] = 0.35
        rows[1]["changed_pixel_ratio"] = 0.80
        rows[1]["histogram_delta"] = 0.85
        events = detect_event_candidates(rows, 10.0)
        self.assertIn("scene_transition_candidate", {e["event_type"] for e in events})

    def test_local_residual_motion_regions_are_localized_without_identity_claim(self):
        rows = [row(i, 0.0, 0.0, 0.0) for i in range(3)]
        grid = []
        for y in range(4):
            for x in range(6):
                active = (y == 1 and x in (2, 3))
                grid.append({
                    "row": y, "column": x,
                    "x0_norm": x / 6.0, "y0_norm": y / 4.0,
                    "x1_norm": (x + 1) / 6.0, "y1_norm": (y + 1) / 4.0,
                    "affine_residual_moving_pixel_ratio": 0.25 if active else 0.0,
                    "affine_residual_p90_magnitude_px_frame": 2.0 if active else 0.1,
                    "affine_residual_mean_magnitude_px_frame": 1.0 if active else 0.0,
                })
        rows[1]["flow_grid"] = grid
        events = detect_event_candidates(rows, 10.0)
        regions = [e for e in events if e["event_type"] == "local_motion_region_candidate"]
        self.assertEqual(len(regions), 1)
        evidence = regions[0]["measurement"]
        self.assertEqual(evidence["cell_count"], 2)
        self.assertEqual(evidence["bbox_norm_xyxy"], [0.3333, 0.25, 0.6667, 0.5])
        self.assertIn("not an object identity", regions[0]["interpretation_limit"])

    def test_exact_duplicate_run_is_flagged_with_caveat(self):
        rows = [row(i, 0.0, 0.0, 0.0) for i in range(12)]
        for i in range(1, 12):
            rows[i]["exact_duplicate_of_previous"] = True
        events = detect_event_candidates(rows, 10.0)
        freezes = [e for e in events if e["event_type"] == "repeated_frame_run_candidate"]
        self.assertEqual(len(freezes), 1)
        self.assertGreaterEqual(freezes[0]["measurement"]["duration_s"], 0.5)
        self.assertIn("intentional hold", freezes[0]["interpretation_limit"])


if __name__ == "__main__":
    unittest.main()
