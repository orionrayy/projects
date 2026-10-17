import tempfile
import unittest
from pathlib import Path

import numpy as np

from motionlab.learning import fit_relational_model, load_model, score_vectors, validation_summary, write_json_atomic


class RelationalLearningTests(unittest.TestCase):
    def setUp(self):
        self.examples = []
        for video in range(6):
            for window in range(5):
                center = np.zeros(24, dtype=np.float64)
                center[video % 3 * 4:(video % 3 + 1) * 4] = 2.0
                vector = center + np.sin(np.arange(24) + window + video * 0.3) * 0.05
                self.examples.append({"video_sha256": f"{video:064x}", "window_index": window, "vector": vector.tolist()})

    def test_fit_score_and_integrity_round_trip(self):
        training = self.examples[:20]
        validation = self.examples[20:]
        model = fit_relational_model(training, max_components=8, max_prototypes=4)
        scores = score_vectors(model, np.asarray([x["vector"] for x in validation]))
        self.assertEqual(len(scores), len(validation))
        self.assertTrue(all(0 <= score["prototype_id"] < len(model["prototypes"]) for score in scores))
        self.assertTrue(all(np.isfinite(score["novelty_ratio"]) for score in scores))
        summary = validation_summary(model, validation)
        self.assertEqual(summary["status"], "COMPUTED")
        self.assertGreaterEqual(summary["occupied_prototype_count"], 1)
        with tempfile.TemporaryDirectory() as tempdir:
            path = write_json_atomic(Path(tempdir) / "model.json", model)
            loaded = load_model(path)
            self.assertEqual(loaded["model_sha256"], model["model_sha256"])

    def test_rejects_nan_training_data(self):
        bad = [{"vector": [float("nan")] * 8}, {"vector": [0.0] * 8}]
        with self.assertRaisesRegex(ValueError, "non_finite"):
            fit_relational_model(bad)

    def test_rejects_feature_dimension_mismatch(self):
        model = fit_relational_model(self.examples[:10], max_components=4, max_prototypes=3)
        with self.assertRaisesRegex(ValueError, "dimension_mismatch"):
            score_vectors(model, np.zeros((2, 9), dtype=np.float64))


if __name__ == "__main__":
    unittest.main()
