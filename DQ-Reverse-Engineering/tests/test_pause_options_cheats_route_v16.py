import json
import tempfile
import unittest
from pathlib import Path

from tools.validate_pause_options_cheats_route_v16 import validate


ROOT = Path(__file__).resolve().parents[1]


class PauseOptionsCheatsRouteV16Tests(unittest.TestCase):
    def test_repository_route_contract_is_explicit_and_fail_closed(self):
        result = validate(ROOT)
        self.assertEqual(result["status"], "PASS", result["errors"])
        self.assertEqual(result["route_binding_status"], "BLOCKED")
        self.assertEqual(result["runtime_verified_claims"], 0)

    def test_manifest_cannot_claim_route_binding_without_hook_evidence(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "runtime-adapter/src/main/java/dev/dqdebug/runtime").mkdir(parents=True)
            manifest_src = ROOT / "docs" / "PAUSE_OPTIONS_CHEATS_ROUTE_V16.json"
            manifest = json.loads(manifest_src.read_text(encoding="utf-8"))
            manifest["route_binding"]["status"] = "RUNTIME-VERIFIED"
            (root / "docs/PAUSE_OPTIONS_CHEATS_ROUTE_V16.json").write_text(
                json.dumps(manifest), encoding="utf-8")
            bridge_src = ROOT / "runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java"
            (root / "runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java").write_text(
                bridge_src.read_text(encoding="utf-8"), encoding="utf-8")
            result = validate(root)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("must remain BLOCKED" in item for item in result["errors"]))

    def test_missing_bridge_contract_marker_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "docs").mkdir()
            (root / "runtime-adapter/src/main/java/dev/dqdebug/runtime").mkdir(parents=True)
            manifest_src = ROOT / "docs" / "PAUSE_OPTIONS_CHEATS_ROUTE_V16.json"
            (root / "docs/PAUSE_OPTIONS_CHEATS_ROUTE_V16.json").write_text(
                manifest_src.read_text(encoding="utf-8"), encoding="utf-8")
            bridge = ROOT / "runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java"
            content = bridge.read_text(encoding="utf-8").replace('PageStatus.READ_ONLY', 'PageStatus.DISABLED')
            (root / "runtime-adapter/src/main/java/dev/dqdebug/runtime/PauseOptionsCheatsBridge.java").write_text(
                content, encoding="utf-8")
            result = validate(root)
        self.assertEqual(result["status"], "FAIL")
        self.assertTrue(any("PageStatus.READ_ONLY" in item for item in result["errors"]))


if __name__ == "__main__":
    unittest.main()
