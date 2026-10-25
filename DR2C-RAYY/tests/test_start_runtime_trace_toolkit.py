from __future__ import annotations
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "runtime_trace" / "Collect-DR2CStartTrace.ps1"
LAUNCHER = ROOT / "tools" / "runtime_trace" / "RUN-TRACE.bat"
DOC = ROOT / "docs" / "START_RUNTIME_TRACE_v2.63.md"


class StartRuntimeTraceToolkitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script = SCRIPT.read_text(encoding="utf-8")
        cls.launcher = LAUNCHER.read_text(encoding="utf-8")
        cls.doc = DOC.read_text(encoding="utf-8")

    def test_collector_targets_expected_package_and_reads_runtime_logs(self):
        self.assertIn("com.noodlecake.drtc", self.script)
        self.assertIn("logcat -c", self.script)
        self.assertIn("'logcat', '-b', 'all', '-v', 'threadtime'", self.script)
        self.assertIn("dumpsys package $PackageName", self.script)
        self.assertIn("dumpsys activity activities", self.script)

    def test_no_destructive_adb_package_or_save_commands(self):
        forbidden = re.compile(
            r"(?im)^\s*&\s*\$adbPath\s+.*\b(?:install|uninstall|clear|disable|enable|grant|revoke)\b"
            r"|^\s*&\s*\$adbPath\s+.*\bam\s+force-stop\b"
            r"|^\s*&\s*\$adbPath\s+.*\brun-as\b"
        )
        self.assertIsNone(forbidden.search(self.script))

    def test_raw_log_is_filtered_then_deleted_before_zip(self):
        filter_pos = self.script.index("Select-String -Path $rawLog")
        delete_pos = self.script.index("Remove-Item $rawLog")
        zip_pos = self.script.index("Compress-Archive")
        self.assertLess(filter_pos, delete_pos)
        self.assertLess(delete_pos, zip_pos)
        self.assertIn("logcat-relevant-lines.txt", self.script)

    def test_error_paths_fail_closed_when_adb_or_device_is_unavailable(self):
        self.assertIn("Get-Command adb", self.script)
        self.assertIn("Tidak ada perangkat berstatus device", self.script)
        self.assertIn("Paket $PackageName tidak terdeteksi", self.script)

    def test_launcher_invokes_the_adjacent_collector(self):
        self.assertIn("-ExecutionPolicy Bypass", self.launcher)
        self.assertIn("Collect-DR2CStartTrace.ps1", self.launcher)

    def test_doc_keeps_runtime_release_gate_blocked_until_trace(self):
        self.assertIn("BLOCKED", self.doc)
        self.assertIn("not yet collected", self.doc)
        self.assertIn("does not", self.doc.lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
