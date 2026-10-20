import contextlib
import io
import shutil
import tempfile
import unittest
from pathlib import Path

from motionlab.synthetic import generate_synthetic_clip
from motionlab.train import corpus_inventory_fingerprint, _split_hashes, watch_corpus


class TrainingWorkflowTests(unittest.TestCase):
    def test_corpus_inventory_checkpoint_is_stable_and_changes_with_input(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            video = root / "clip.mp4"
            video.write_bytes(b"synthetic-video-a")
            first, count_first = corpus_inventory_fingerprint(root)
            second, count_second = corpus_inventory_fingerprint(root)
            self.assertEqual(first, second)
            self.assertEqual(count_first, 1)
            self.assertEqual(count_second, 1)
            video.write_bytes(b"synthetic-video-b-with-new-size")
            third, count_third = corpus_inventory_fingerprint(root)
            self.assertNotEqual(first, third)
            self.assertEqual(count_third, 1)

    def test_source_split_is_disjoint_and_reproducible(self):
        hashes = [f"{number:064x}" for number in range(10)]
        train_a, val_a = _split_hashes(hashes)
        train_b, val_b = _split_hashes(list(reversed(hashes)))
        self.assertTrue(train_a)
        self.assertTrue(val_a)
        self.assertTrue(train_a.isdisjoint(val_a))
        self.assertEqual(train_a, train_b)
        self.assertEqual(val_a, val_b)


    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg/FFprobe are required")
    def test_watch_checkpoints_failed_promotion_and_skips_unchanged_corpus(self):
        with tempfile.TemporaryDirectory() as tempdir:
            root = Path(tempdir)
            corpus = root / "videos"
            corpus.mkdir()
            generate_synthetic_clip(
                corpus / "static-fixture.mkv",
                scenario="static",
                duration_s=2.0,
                fps=4,
                width=64,
                height=64,
            )
            output = root / "models"
            options = {
                "max_videos": 1,
                "max_fps": 4.0,
                "width": 64,
                "height": 64,
                "max_frames": 100,
                "window_frames": 4,
                "window_stride": 2,
                "max_components": 4,
                "max_prototypes": 2,
                "encoder_hidden_dim": 4,
                "encoder_epochs": 1,
                "max_windows_per_video": 4,
                "auto_promote": True,
                "rights_attested": True,
            }
            with contextlib.redirect_stdout(io.StringIO()):
                first = watch_corpus(
                    corpus, output, poll_interval_s=30, retry_interval_s=3600,
                    max_cycles=1, **options,
                )
            self.assertEqual(first["status"], "CANDIDATE_NEEDS_EVIDENCE")
            self.assertTrue((output / "watch_state.json").is_file())
            self.assertTrue((output / "candidate_model.json").is_file())
            self.assertFalse((output / "active_model.json").exists())

            with contextlib.redirect_stdout(io.StringIO()):
                second = watch_corpus(
                    corpus, output, poll_interval_s=30, retry_interval_s=3600,
                    max_cycles=1, **options,
                )
            self.assertEqual(second["status"], "UNCHANGED_SKIPPED")
            self.assertFalse((output / "active_model.json").exists())


if __name__ == "__main__":
    unittest.main()
