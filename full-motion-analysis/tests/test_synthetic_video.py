import shutil
import tempfile
import unittest
from pathlib import Path

from motionlab.analysis import analyze_video
from motionlab.audit import audit_video
from motionlab.synthetic import generate_synthetic_clip


TOOLS_AVAILABLE = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


@unittest.skipUnless(TOOLS_AVAILABLE, "FFmpeg/FFprobe are required for integration tests")
class SyntheticSpaceTimeTests(unittest.TestCase):
    def test_open_world_reports_cover_multiple_synthetic_domains(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            scenarios = ("move_reverse", "freeze", "flash", "global_pan_reverse", "pan_plus_object", "abstract_nirmana", "fractal_zoom")
            reports = []
            for scenario in scenarios:
                clip = generate_synthetic_clip(
                    root / f"{scenario}.mkv", scenario=scenario, duration_s=2.0, fps=15
                )
                report = analyze_video(
                    clip, max_fps=15, width=128, height=72,
                    window_frames=16, window_stride=8, optical_flow=True,
                )
                reports.append(report)
                self.assertEqual(report["schema_version"], "fma.openworld.analysis.v0.2")
                self.assertFalse(report["sampling"]["pairwise_frame_analysis_is_primary"])
                self.assertGreaterEqual(report["sampling"]["frames_decoded"], 25)
                self.assertGreaterEqual(report["sampling"]["timeline_coverage_ratio"], 0.95)
                self.assertGreaterEqual(report["measurements"]["feature_dimensions"], 120)
                self.assertEqual(report["measurements"]["region_node_count_per_window"], 24)
                self.assertEqual(len(report["relational_field"]["cross_window_relations"]) <= 512, True)
                self.assertEqual(len(report["input"]["sha256"]), 64)
                windows = report["timeline"]
                centers = [item["center_timestamp_s"] for item in windows]
                self.assertEqual(centers, sorted(set(centers)))
                self.assertTrue(all(len(item["signature_vector"]) == report["measurements"]["feature_dimensions"] for item in windows))
                self.assertTrue(all(len(item["scale_signatures"]) == 3 for item in windows))
                self.assertFalse(report["provenance"]["legacy_pairwise_optical_flow_used_by_core"])

            freeze_report = reports[1]
            self.assertGreater(freeze_report["measurements"]["exact_duplicate_transition_ratio"], 0.30)
            self.assertIn("repeated_frame_run_candidate", {event["event_type"] for event in freeze_report["events"]})
            flash_report = reports[2]
            self.assertGreater(flash_report["measurements"]["signature_distance_p95"], 0.0)
            self.assertIn("possible_flash_candidate", {event["event_type"] for event in flash_report["events"]})
            mixed_report = reports[4]
            abstract_report = reports[5]
            fractal_report = reports[6]
            self.assertEqual(mixed_report["relational_field"]["unit"], "space_time_window")
            self.assertTrue(mixed_report["timeline"])
            self.assertGreater(abstract_report["measurements"]["signature_distance_p95"], 0.0)
            self.assertGreater(fractal_report["measurements"]["signature_distance_p95"], 0.0)
            self.assertEqual(abstract_report["sampling"]["pairwise_frame_analysis_is_primary"], False)
            self.assertEqual(fractal_report["sampling"]["pairwise_frame_analysis_is_primary"], False)


    @unittest.skipUnless(TOOLS_AVAILABLE, "FFmpeg/FFprobe are required for integration tests")
    def test_luma_pulse_reaches_ffmpeg_render_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            clip = generate_synthetic_clip(
                Path(directory) / "flash-audit.mkv",
                scenario="flash", duration_s=2.0, fps=12, width=128, height=72,
            )
            report = audit_video(clip, max_fps=12)
            codes = {finding["code"] for finding in report["qc"]["findings"]}
            self.assertIn("FMA-QC-FLASH-CANDIDATE", codes)


if __name__ == "__main__":
    unittest.main()
