import os, struct, unittest, pathlib, sys
HERE = pathlib.Path(__file__).resolve().parent
TOOLS = HERE.parent / "tools"
sys.path.insert(0, str(TOOLS if TOOLS.is_dir() else HERE))
SOURCE_ASSETS = pathlib.Path(os.environ["DQ_SOURCE_ASSETS"]) if os.environ.get("DQ_SOURCE_ASSETS") else None
from hud_action_probe_v45 import parse_action_section, HudActionFormatError, tagged_values, inspect_hud

def s(value: bytes) -> bytes:
    return struct.pack("<I", len(value)) + value

class HudActionProbeV45Tests(unittest.TestCase):
    def test_empty_actions(self):
        result = parse_action_section(b"\x00\x00")
        self.assertEqual(result["action_count"], 0)
        self.assertEqual(result["actions"], [])

    def test_multiple_statements_and_terminator(self):
        first = b"<004><4,5>pause"
        second = b"<023><2,10>uai_gp_hud<2,7>onDebug"
        data = struct.pack("<H", 1) + s(b"onShow") + struct.pack("<H", 2) + s(first) + s(second) + struct.pack("<I", 0)
        result = parse_action_section(data)
        action = result["actions"][0]
        self.assertEqual(action["name"], "onShow")
        self.assertEqual(action["declared_statement_count"], 2)
        self.assertEqual(action["statements"], [first.decode(), second.decode()])

    def test_tagged_values_bounded(self):
        values = tagged_values("<023><2,10>uai_gp_hud<2,7>onDebug")
        self.assertEqual([x["value"] for x in values], ["uai_gp_hud", "onDebug"])
        self.assertEqual(tagged_values("<2,100>short"), [])

    def test_truncated_statement_rejected(self):
        data = struct.pack("<H", 1) + s(b"onClick") + struct.pack("<H", 1) + struct.pack("<I", 8) + b"abc"
        with self.assertRaises(HudActionFormatError):
            parse_action_section(data)

    def test_early_terminator_rejected(self):
        data = struct.pack("<H", 1) + s(b"onClick") + struct.pack("<H", 1) + struct.pack("<I", 0)
        with self.assertRaises(HudActionFormatError):
            parse_action_section(data)

    def test_trailing_bytes_rejected(self):
        with self.assertRaises(HudActionFormatError):
            parse_action_section(b"\x00\x00X")

    def test_real_debug_hud_actions(self):
        if SOURCE_ASSETS is None:
            self.skipTest("set DQ_SOURCE_ASSETS to run source-asset integration assertions")
        path = SOURCE_ASSETS / "Resources/HUD/debug.hud"
        if not path.exists():
            self.skipTest("extracted game assets are unavailable")
        report = inspect_hud(path)
        self.assertEqual(report["action_count"], 13)
        names = {a["name"]: a for a in report["actions"]}
        self.assertEqual(names["onAddLevel"]["statement_count"], 1)
        values = [v["value"] for v in names["onAddLevel"]["tagged_values"]]
        self.assertIn("uai_gp_hud", values)
        self.assertIn("onDebug", values)

    def test_real_pause_has_multi_statement_action(self):
        if SOURCE_ASSETS is None:
            self.skipTest("set DQ_SOURCE_ASSETS to run source-asset integration assertions")
        path = SOURCE_ASSETS / "Resources/HUD/pause.hud"
        if not path.exists():
            self.skipTest("extracted game assets are unavailable")
        report = inspect_hud(path)
        self.assertEqual(report["action_count"], 64)
        names = {a["name"]: a for a in report["actions"]}
        self.assertEqual(names["onShowPause"]["statement_count"], 2)

if __name__ == "__main__":
    unittest.main()
