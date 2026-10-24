import importlib.util
import struct
import unittest
from pathlib import Path

TOOL = Path(__file__).resolve().parents[1] / "tools" / "patch_pause_cheats_sandbox_v21.py"
spec = importlib.util.spec_from_file_location("pause_patch_v21", TOOL)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixture(version=12, label="Social/IAP", valid_schema=True):
    general = mod.lp("boot")
    elements = struct.pack("<I", 126) + mod.lp(label) + mod.lp("onShowSocial")
    params = ["p1","p2","p3","p4","p5","p6", mod.EXPECTED_LAST]
    if not valid_schema:
        params[-1] = "different"
    actions = [
        {"name":"onResume","parameters":["resume-script"],"extra_script":""},
        {"name":"onShowSocial","parameters":params,"extra_script":""},
        {"name":"untouched","parameters":["keep-me"],"extra_script":"none"},
    ]
    payload = bytearray(struct.pack("<H", len(actions)))
    for action in actions:
        payload += mod.write_action(action, version)
    sections = {
        "general_attributes": general, "elements": elements,
        "actions": bytes(payload), "timers": struct.pack("<H", 0)
    }
    result = bytearray(struct.pack("<I", 3) + b"NcP" + bytes([version]))
    for name in mod.SECTIONS:
        result += struct.pack("<I", len(sections[name])) + sections[name]
    return bytes(result)

class PauseCheatsAssetPatchV21Tests(unittest.TestCase):
    def test_button_and_callback_are_patched(self):
        patched, report = mod.patch_hud(fixture())
        sec, version = mod.sections(patched)
        actions = mod.parse_actions(sec["actions"], version)
        self.assertIn(mod.lp("Cheats Sandbox"), sec["elements"])
        self.assertIn(mod.lp("onShowCheats"), sec["elements"])
        target = next(a for a in actions if a["name"] == "onShowCheats")
        self.assertEqual(target["parameters"], [mod.RESUME, mod.DEBUG])
        self.assertEqual(len(actions), 3)
        self.assertTrue(report["unrelated_actions_preserved"])

    def test_unrelated_actions_and_sections_remain_unchanged(self):
        source = fixture()
        before, ver = mod.sections(source)
        old = mod.parse_actions(before["actions"], ver)
        patched, _ = mod.patch_hud(source)
        after, ver2 = mod.sections(patched)
        new = mod.parse_actions(after["actions"], ver2)
        self.assertEqual(before["general_attributes"], after["general_attributes"])
        self.assertEqual(before["timers"], after["timers"])
        for a, b in zip(old, new):
            if a["name"] == "onShowSocial":
                self.assertEqual(b["name"], "onShowCheats")
            else:
                self.assertEqual(a, b)

    def test_wrong_version_fails_closed(self):
        with self.assertRaises(mod.PatchError):
            mod.patch_hud(fixture(version=11))

    def test_missing_label_or_schema_mismatch_fails_closed(self):
        with self.assertRaises(mod.PatchError):
            mod.patch_hud(fixture(label="Not the audited label"))
        with self.assertRaises(mod.PatchError):
            mod.patch_hud(fixture(valid_schema=False))

if __name__ == "__main__":
    unittest.main()
