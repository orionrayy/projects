import struct, pathlib, sys, unittest

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
TOOLS = ROOT / "tools"
sys.path.insert(0, str(TOOLS if TOOLS.is_dir() else HERE))
from hud_action_probe_v45 import parse_action_section, HudActionFormatError
from hud_action_serializer_v46 import encode_action_section, append_action

def s(value: bytes) -> bytes:
    return struct.pack("<I", len(value)) + value

def sample() -> bytes:
    one = b"<023><2,10>uai_gp_hud<2,7>onDebug"
    two = b"<004><4,5>pause"
    return (struct.pack("<H", 2) + s(b"onClick") + struct.pack("<H", 1) +
            s(one) + struct.pack("<I", 0) + s(b"onShow") +
            struct.pack("<H", 2) + s(two) + s(one) + struct.pack("<I", 0))

class HudActionSerializerV46Tests(unittest.TestCase):
    def test_exact_noop_roundtrip(self):
        raw = sample()
        self.assertEqual(encode_action_section(parse_action_section(raw)), raw)

    def test_append_single_statement(self):
        doc = parse_action_section(sample())
        append_action(doc, "onGold", ["<023><8,3>013<2,10>uai_gp_hud<2,7>onDebug<1,5>6.000"])
        rebuilt = encode_action_section(doc)
        decoded = parse_action_section(rebuilt)
        self.assertEqual(decoded["action_count"], 3)
        self.assertEqual(decoded["actions"][-1]["name"], "onGold")
        self.assertEqual(decoded["actions"][-1]["statement_count"], 1)

    def test_duplicate_action_rejected(self):
        doc = parse_action_section(sample())
        with self.assertRaises(HudActionFormatError):
            append_action(doc, "onClick", ["x"])

    def test_inconsistent_declared_count_rejected(self):
        doc = parse_action_section(sample())
        doc["actions"][0]["declared_statement_count"] = 2
        with self.assertRaises(HudActionFormatError):
            encode_action_section(doc)

    def test_invalid_empty_statement_rejected(self):
        doc = parse_action_section(sample())
        doc["actions"][0]["statements"] = [""]
        doc["actions"][0]["declared_statement_count"] = 1
        with self.assertRaises(HudActionFormatError):
            encode_action_section(doc)

if __name__ == "__main__":
    unittest.main()
