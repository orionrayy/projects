#!/usr/bin/env python3
from __future__ import annotations
import copy, json, pathlib, sys, unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from validate_no_native_probe_comparator_v73 import AuditError, validate
REPORT=ROOT/"docs"/"NO_NATIVE_PROBE_COMPARATOR_V73.json"

class NoNativeProbeComparatorV73Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base=json.loads(REPORT.read_text(encoding="utf-8"))
    def test_pinned_report_passes_and_runtime_is_blocked(self):
        out=validate(copy.deepcopy(self.base))
        self.assertEqual(out["status"],"PASS_STATIC_V73_COMPARATOR_REPORT")
        self.assertFalse(out["device_runtime_tested"])
        self.assertFalse(out["native_probe_present"])
        self.assertFalse(out["promotion_allowed"])
    def test_apk_identity_is_pinned(self):
        doc=copy.deepcopy(self.base); doc["artifact"]["sha256"]="0"*64
        with self.assertRaisesRegex(AuditError,"artifact SHA-256"): validate(doc)
        doc=copy.deepcopy(self.base); doc["artifact"]["package_id"]="com.shinybox.smash"
        with self.assertRaisesRegex(AuditError,"package ID"): validate(doc)
    def test_probe_must_be_absent_and_stock_dex_pinned(self):
        doc=copy.deepcopy(self.base); doc["isolation_changes"]["libdqbridge_removed"]=False
        with self.assertRaisesRegex(AuditError,"probe library removal"): validate(doc)
        doc=copy.deepcopy(self.base); doc["inputs"]["stock_dex_sha256"]="0"*64
        with self.assertRaisesRegex(AuditError,"stock DEX hash"): validate(doc)
    def test_gold_hud_asset_is_preserved(self):
        doc=copy.deepcopy(self.base); doc["isolation_changes"]["gold_hud_stk_preserved"]=False
        with self.assertRaisesRegex(AuditError,"Gold HUD asset"): validate(doc)
        doc=copy.deepcopy(self.base); doc["inputs"]["stk_sha256"]="0"*64
        with self.assertRaisesRegex(AuditError,"STK hash"): validate(doc)
    def test_static_gates_are_fail_closed(self):
        for key in ("zip_crc","zipalign_16k_pre_sign","zipalign_16k_post_sign",
                    "apksigner_v1","apksigner_v2","apksigner_v3","aapt_badging"):
            doc=copy.deepcopy(self.base); doc["static_validation"][key]="FAIL"
            with self.subTest(key=key), self.assertRaisesRegex(AuditError,"static validation"): validate(doc)
    def test_runtime_must_not_be_fabricated(self):
        for key in ("device_install_tested","device_start_tested","force_close_reproduced_or_cleared","native_callback_invoked"):
            doc=copy.deepcopy(self.base); doc["runtime"][key]=True
            with self.subTest(key=key), self.assertRaisesRegex(AuditError,"must not claim runtime"): validate(doc)
        doc=copy.deepcopy(self.base); doc["promotion_allowed"]=True
        with self.assertRaisesRegex(AuditError,"must not be promoted"): validate(doc)
    def test_private_key_and_official_signer_claims_are_rejected(self):
        doc=copy.deepcopy(self.base); doc["signing"]["private_key_shared"]=True
        with self.assertRaisesRegex(AuditError,"private key"): validate(doc)
        doc=copy.deepcopy(self.base); doc["signing"]["matches_official_signer"]=True
        with self.assertRaisesRegex(AuditError,"official signer"): validate(doc)
    def test_physical_device_limitation_is_required(self):
        doc=copy.deepcopy(self.base); doc["limitations"]=["static only"]
        with self.assertRaisesRegex(AuditError,"physical-device limitation"): validate(doc)

if __name__=="__main__": unittest.main(verbosity=2)
