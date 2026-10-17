import tempfile
import unittest
from pathlib import Path

from motionlab.train import corpus_inventory_fingerprint, _split_hashes


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


if __name__ == "__main__":
    unittest.main()
