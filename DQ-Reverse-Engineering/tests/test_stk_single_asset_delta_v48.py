from __future__ import annotations
import hashlib, pathlib, struct, tempfile, unittest, zlib, sys
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"tools"))
from verify_stk_single_asset_delta_v48 import verify_delta
from stk_packer import HEADER, ENTRY_META, xor_bytes

def make_stk(entries: dict[str, bytes], key: int = 0x12345678) -> bytes:
    payloads=[]
    for name, data in entries.items():
        compressed=zlib.compress(data,9)
        stored=compressed if len(compressed)<len(data) else data
        payloads.append((name, data, stored))
    table=bytearray()
    offset=0
    for name, raw, stored in payloads:
        nb=name.encode("utf-8")
        table.extend(struct.pack("<I",len(nb)))
        table.extend(nb)
        table.extend(ENTRY_META.pack(offset,len(stored),len(raw),zlib.crc32(stored)&0xffffffff,0))
        offset += len(stored)
    table_end=HEADER.size+len(table)
    header=HEADER.pack(6,0x8,b"v48test!",key,len(payloads),table_end)
    return header+xor_bytes(bytes(table),key)+b"".join(xor_bytes(stored,key) for _,_,stored in payloads)

class StkSingleAssetDeltaV48Tests(unittest.TestCase):
    def write(self, root: pathlib.Path, name: str, data: bytes) -> pathlib.Path:
        path=root/name
        path.write_bytes(data)
        return path

    def test_exactly_one_expected_asset_changed(self):
        src={"Resources/HUD/debug.hud":b"debug:stock","Resources/HUD/pause.hud":b"pause:stock","Resources/AIModels/uai_gp_hud.aim":b"model"}
        dst=dict(src); dst["Resources/HUD/debug.hud"]=b"debug:modified"
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=self.write(root,"source.smf",make_stk(src))
            candidate=self.write(root,"candidate.smf",make_stk(dst))
            report=verify_delta(source,candidate)
            self.assertEqual(report["status"],"PASS")
            self.assertEqual(report["changed_entry_count"],1)
            self.assertEqual(report["changed_entries"][0]["path"],"Resources/HUD/debug.hud")
            self.assertTrue(report["all_unchanged_decoded_entries_identical"])

    def test_rejects_two_changed_assets(self):
        src={"Resources/HUD/debug.hud":b"a","Resources/HUD/pause.hud":b"b"}
        dst={"Resources/HUD/debug.hud":b"aa","Resources/HUD/pause.hud":b"bb"}
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=self.write(root,"source.smf",make_stk(src))
            candidate=self.write(root,"candidate.smf",make_stk(dst))
            with self.assertRaisesRegex(ValueError,"exactly one changed asset"):
                verify_delta(source,candidate)

    def test_rejects_wrong_changed_asset(self):
        src={"Resources/HUD/debug.hud":b"a","Resources/HUD/pause.hud":b"b"}
        dst={"Resources/HUD/debug.hud":b"a","Resources/HUD/pause.hud":b"bb"}
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=self.write(root,"source.smf",make_stk(src))
            candidate=self.write(root,"candidate.smf",make_stk(dst))
            with self.assertRaisesRegex(ValueError,"exactly one changed asset"):
                verify_delta(source,candidate)

    def test_rejects_entry_inventory_change(self):
        src={"Resources/HUD/debug.hud":b"a","Resources/HUD/pause.hud":b"b"}
        dst={"Resources/HUD/debug.hud":b"aa","Resources/HUD/new.hud":b"new"}
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=self.write(root,"source.smf",make_stk(src))
            candidate=self.write(root,"candidate.smf",make_stk(dst))
            with self.assertRaisesRegex(ValueError,"entry inventory differs"):
                verify_delta(source,candidate)

    def test_source_sha256_pin_is_enforced(self):
        src={"Resources/HUD/debug.hud":b"a"}
        dst={"Resources/HUD/debug.hud":b"b"}
        with tempfile.TemporaryDirectory() as tmp:
            root=pathlib.Path(tmp)
            source=self.write(root,"source.smf",make_stk(src))
            candidate=self.write(root,"candidate.smf",make_stk(dst))
            with self.assertRaisesRegex(ValueError,"source SHA-256 mismatch"):
                verify_delta(source,candidate,expected_source_sha256="0"*64)

    def test_same_input_output_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path=self.write(pathlib.Path(tmp),"same.smf",make_stk({"Resources/HUD/debug.hud":b"a"}))
            with self.assertRaisesRegex(ValueError,"must be different"):
                verify_delta(path,path)

if __name__=="__main__":
    unittest.main()
