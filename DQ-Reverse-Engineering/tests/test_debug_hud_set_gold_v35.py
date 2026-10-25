import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from patch_debug_hud_set_gold_v35 import patch, parse_hud, serialize_hud, serialize_actions, parse_actions


def action(name):
    return {"name": name, "params": [], "script": ""}


def make_button_record(size=193):
    rec = bytearray(size)
    name = b"gold_minus_10_btn"
    struct.pack_into("<I", rec, 0, len(name))
    rec[4:4 + len(name)] = name
    # Put the visible label and callback identifier into the record in their expected fields.
    label = b"Gold -10"
    struct.pack_into("<I", rec, 128, len(label))
    rec[132:132 + len(label)] = label
    cb = b"onGoldMinus10"
    struct.pack_into("<I", rec, 176, len(cb))
    rec[180:180 + len(cb)] = cb
    # A known sentinel byte just before the transform proves the off-by-one was not repeated.
    rec[33] = 0x80
    return bytes(rec)


def make_hud(elements, actions):
    return serialize_hud(b"NcP", 12, [b"\0\0\0\0", elements, serialize_actions(actions), b"\0\0"])


class SetGoldV35PatcherTests(unittest.TestCase):
    def build_inputs(self):
        original_elements = bytearray(32)
        struct.pack_into("<I", original_elements, 0, 71)
        for i in range(4, len(original_elements)):
            original_elements[i] = (i * 7) & 0xff

        v33_prefix = bytearray(original_elements)
        struct.pack_into("<I", v33_prefix, 0, 75)
        # Simulate a layout adjustment inside the unchanged-length original element prefix.
        v33_prefix[9] ^= 0x5a

        button = make_button_record(193)
        extras = [button, b"A" * 190, b"B" * 188, b"C" * 191]
        v33_elements = bytes(v33_prefix) + b"".join(extras)

        orig_actions = [action(f"original_{i}") for i in range(13)]
        v33_actions = orig_actions + [action("onGoldMinus10"), action("onGoldMinus1"),
                                      action("onGoldPlus1"), action("onGoldPlus10")]
        original = make_hud(bytes(original_elements), orig_actions)
        v33 = make_hud(v33_elements, v33_actions)
        return original, v33, bytes(v33_prefix), button

    def test_replaces_four_mini_controls_with_one_corrected_set_gold(self):
        original, v33, v33_prefix, source_button = self.build_inputs()
        output, report = patch(original, v33)
        _, _, sections = parse_hud(output)
        elements, actions = sections[1], parse_actions(sections[2])
        self.assertEqual(struct.unpack_from("<I", elements)[0], 72)
        self.assertEqual(len(actions), 14)
        self.assertEqual(elements[4:len(v33_prefix)], v33_prefix[4:])
        appended = elements[len(v33_prefix):]
        self.assertIn(b"Set Gold", appended)
        self.assertNotIn(b"Gold -10", appended)
        self.assertEqual(actions[-1]["name"], "onGoldMinus10")
        self.assertIn("uai_gp_hud", actions[-1]["params"][0])
        self.assertIn("onSetGold", actions[-1]["params"][0])
        self.assertEqual(report["correct_transform_offsets"], [34, 38, 42, 46])
        self.assertTrue(report["preserves_v33_layout_prefix"])

    def test_transform_offsets_leave_preceding_metadata_byte_untouched(self):
        original, v33, prefix, source_button = self.build_inputs()
        output, _ = patch(original, v33)
        _, _, sections = parse_hud(output)
        record = sections[1][len(prefix):]
        self.assertEqual(record[33], 0x80)
        self.assertEqual(struct.unpack_from("<4f", record, 34),
                         (0.0, -0.7900000214576721, 0.8199999928474426, 0.18000000715255737))

    def test_rejects_wrong_source_counts(self):
        original, v33, _, _ = self.build_inputs()
        _, _, sections = parse_hud(original)
        bad_elements = bytearray(sections[1])
        struct.pack_into("<I", bad_elements, 0, 70)
        bad_original = make_hud(bytes(bad_elements), parse_actions(sections[2]))
        with self.assertRaisesRegex(ValueError, "original HUD element count mismatch"):
            patch(bad_original, v33)


if __name__ == "__main__":
    unittest.main()
