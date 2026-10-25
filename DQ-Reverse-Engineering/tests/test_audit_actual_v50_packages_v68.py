from __future__ import annotations
import pathlib, struct, tempfile, unittest, zlib, sys

TOOLS=pathlib.Path(__file__).resolve().parents[1]/"tools"
sys.path.insert(0,str(TOOLS))
from audit_actual_v50_packages_v68 import (
    AuditError, changed_payload_paths, compare_stk, is_signing_metadata,
)
from stk_packer import HEADER, ENTRY_META, xor_bytes

def make_stk(entries: dict[str,bytes], key: int=0x12345678) -> bytes:
    packed=[]
    for name,data in entries.items():
        compressed=zlib.compress(data,9)
        stored=compressed if len(compressed)<len(data) else data
        packed.append((name,data,stored))
    table=bytearray(); offset=0
    for name,raw,stored in packed:
        encoded=name.encode("utf-8")
        table.extend(struct.pack("<I",len(encoded)))
        table.extend(encoded)
        table.extend(ENTRY_META.pack(offset,len(stored),len(raw),zlib.crc32(stored)&0xffffffff,0))
        offset+=len(stored)
    end=HEADER.size+len(table)
    return HEADER.pack(6,0x8,b"v68test!",key,len(packed),end)+xor_bytes(bytes(table),key)+b"".join(xor_bytes(x[2],key) for x in packed)

class ActualV50PackageAuditTests(unittest.TestCase):
    def test_signature_metadata_exclusions_are_narrow(self):
        for name in ("META-INF/MANIFEST.MF","META-INF/CERT.SF","META-INF/CERT.RSA","META-INF/SIG-FOO"):
            self.assertTrue(is_signing_metadata(name), name)
        for name in ("assets/S3DMain.smf","META-INF/services/provider","META-INF/NOTICE.txt","classes.dex"):
            self.assertFalse(is_signing_metadata(name), name)

    def test_payload_map_detects_added_removed_and_modified_paths(self):
        left={"a": "1", "b":"2"}
        right={"a":"1", "b":"3", "c":"4"}
        self.assertEqual(changed_payload_paths(left,right),["b","c"])

    def test_exact_expected_pause_hud_delta_passes(self):
        src={"Resources/HUD/pause.hud":b"stock-pause","Resources/HUD/debug.hud":b"stock-debug",
             "Resources/AIModels/uai_gp_hud.aim":b"model"}
        dst=dict(src); dst["Resources/HUD/pause.hud"]=b"candidate-pause"
        report=compare_stk(make_stk(src),make_stk(dst))
        self.assertEqual(report["changed_entries"][0]["path"],"Resources/HUD/pause.hud")
        self.assertEqual(report["entry_count"],3)
        self.assertTrue(report["all_unchanged_entries_identical"])

    def test_wrong_stk_asset_delta_fails_closed(self):
        src={"Resources/HUD/pause.hud":b"p","Resources/HUD/debug.hud":b"d"}
        dst=dict(src); dst["Resources/HUD/debug.hud"]=b"debug-changed"
        with self.assertRaisesRegex(AuditError,"expected only Resources/HUD/pause.hud"):
            compare_stk(make_stk(src),make_stk(dst))

    def test_two_stk_changes_fail_closed(self):
        src={"Resources/HUD/pause.hud":b"p","Resources/HUD/debug.hud":b"d"}
        dst={"Resources/HUD/pause.hud":b"pp","Resources/HUD/debug.hud":b"dd"}
        with self.assertRaisesRegex(AuditError,"expected only"):
            compare_stk(make_stk(src),make_stk(dst))

    def test_entry_inventory_change_fails_closed(self):
        src={"Resources/HUD/pause.hud":b"p","Resources/HUD/debug.hud":b"d"}
        dst={"Resources/HUD/pause.hud":b"pp","Resources/HUD/new.hud":b"new"}
        with self.assertRaisesRegex(AuditError,"STK entry inventory differs"):
            compare_stk(make_stk(src),make_stk(dst))

    def test_corrupt_stk_payload_crc_fails_closed(self):
        src=bytearray(make_stk({"Resources/HUD/pause.hud":b"same"}))
        src[-1]^=0x01
        with self.assertRaisesRegex(ValueError,"CRC mismatch|zlib"):
            compare_stk(bytes(src),make_stk({"Resources/HUD/pause.hud":b"changed"}))

if __name__=="__main__":
    unittest.main(verbosity=2)
