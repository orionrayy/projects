import unittest

import numpy as np

from motionlab.relational import FEATURE_SCHEMA, extract_block_signature


def moving_shape(frames=16, height=64, width=96, reverse=False):
    volume = np.zeros((frames, height, width, 3), dtype=np.uint8)
    sequence = range(frames - 1, -1, -1) if reverse else range(frames)
    for output_t, logical_t in enumerate(sequence):
        x = 6 + int(logical_t * (width - 24) / max(1, frames - 1))
        volume[output_t, 22:42, x:x + 18, 0] = 245
        volume[output_t, 22:42, x:x + 18, 1] = 80
        volume[output_t, 22:42, x:x + 18, 2] = 35
    return volume


class OpenWorldRelationalTests(unittest.TestCase):
    def test_space_time_block_produces_multiscale_relational_signature(self):
        result = extract_block_signature(moving_shape())
        self.assertEqual(result["feature_schema"], FEATURE_SCHEMA)
        self.assertGreater(result["feature_count"], 120)
        self.assertEqual(len(result["feature_names"]), result["feature_count"])
        self.assertEqual(len(result["signature_vector"]), result["feature_count"])
        self.assertEqual([x["spatial_scale"] for x in result["scale_signatures"]], [1, 2, 4])
        self.assertEqual(len(result["regional_nodes"]), 24)
        self.assertGreaterEqual(len(result["regional_edges"]), 38)
        self.assertTrue(np.isfinite(np.asarray(result["signature_vector"])).all())

    def test_temporal_reversal_changes_whole_block_signature(self):
        forward = np.asarray(extract_block_signature(moving_shape())["signature_vector"])
        reversed_order = np.asarray(extract_block_signature(moving_shape(reverse=True))["signature_vector"])
        # The representation includes signed interval-level asymmetry, not just order-invariant energy.
        self.assertGreater(float(np.mean(np.abs(forward - reversed_order))), 1e-4)

    def test_color_structure_is_not_discarded(self):
        red = np.zeros((16, 64, 96, 3), dtype=np.uint8)
        blue = red.copy()
        red[..., 0] = 255
        blue[..., 2] = 255
        red_sig = np.asarray(extract_block_signature(red)["signature_vector"])
        blue_sig = np.asarray(extract_block_signature(blue)["signature_vector"])
        self.assertGreater(float(np.mean(np.abs(red_sig - blue_sig))), 0.01)

    def test_static_block_is_finite_even_when_spectrum_is_degenerate(self):
        static = np.zeros((16, 64, 96, 3), dtype=np.uint8)
        static[:, 12:52, 22:74, :] = 150
        result = extract_block_signature(static)
        self.assertTrue(np.isfinite(np.asarray(result["signature_vector"])).all())
        self.assertEqual(len(result["regional_nodes"]), 24)

    def test_rejects_invalid_volume_contract(self):
        with self.assertRaisesRegex(ValueError, "volume_must_be_uint8_T_H_W_RGB"):
            extract_block_signature(np.zeros((16, 64, 96), dtype=np.uint8))
        with self.assertRaisesRegex(ValueError, "space_time_block_too_small"):
            extract_block_signature(np.zeros((1, 64, 96, 3), dtype=np.uint8))


if __name__ == "__main__":
    unittest.main()
