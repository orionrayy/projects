import shutil
import tempfile
import unittest
from pathlib import Path

from motionlab.analysis import analyze_video
from motionlab.synthetic import generate_synthetic_clip


TOOLS_AVAILABLE = bool(shutil.which("ffmpeg") and shutil.which("ffprobe"))


@unittest.skipUnless(TOOLS_AVAILABLE, "FFmpeg/FFprobe are required for integration tests")
class SyntheticVideoTests(unittest.TestCase):
    def test_move_freeze_and_flash_synthetic_contract(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            moving = generate_synthetic_clip(root / "moving.mkv", scenario="move_reverse", duration_s=2.0, fps=15)
            frozen = generate_synthetic_clip(root / "frozen.mkv", scenario="freeze", duration_s=2.0, fps=15)
            flash = generate_synthetic_clip(root / "flash.mkv", scenario="flash", duration_s=2.0, fps=15)

            moving_report = analyze_video(moving, max_fps=15, optical_flow=False)
            frozen_report = analyze_video(frozen, max_fps=15, optical_flow=False)
            flash_report = analyze_video(flash, max_fps=15, optical_flow=False)

            self.assertEqual(moving_report["sampling"]["frames_decoded"], 30)
            self.assertGreater(moving_report["measurements"]["mean_abs_diff_p95"], 0.0005)
            self.assertGreater(frozen_report["measurements"]["exact_duplicate_transition_ratio"], 0.30)
            event_types = {e["event_type"] for e in flash_report["events"]}
            self.assertTrue({"possible_flash_candidate", "scene_transition_candidate"} & event_types)
            for report in (moving_report, frozen_report, flash_report):
                ts = [item["timestamp_s"] for item in report["timeline"]]
                self.assertEqual(ts, sorted(set(ts)))
                self.assertEqual(len(report["input"]["sha256"]), 64)
                self.assertGreaterEqual(report["sampling"]["timeline_coverage_ratio"], 0.95)


if __name__ == "__main__":
    unittest.main()
