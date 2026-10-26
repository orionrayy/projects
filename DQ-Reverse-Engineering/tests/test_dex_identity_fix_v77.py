import hashlib, struct, unittest, zlib
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from build_dex_identity_fix_v77 import patch_dex

class DexIdentityPatchTests(unittest.TestCase):
    def synthetic_dex(self, literal=b"com.shinybox.smash"):
        data=bytearray(160)
        data[:8]=b"dex\\n035\\0"
        struct.pack_into("<I",data,32,len(data))
        struct.pack_into("<I",data,36,0x70)
        data[48:48+len(literal)]=literal
        return bytes(data)

    def test_patch_replaces_literal_and_recomputes_header(self):
        before=self.synthetic_dex()
        after,report=patch_dex(before)
        self.assertEqual(after.count(b"com.shinybox.smash"),0)
        self.assertEqual(after.count(b"com.shinybox.dqv77"),1)
        self.assertEqual(after[12:32],hashlib.sha1(after[32:]).digest())
        self.assertEqual(struct.unpack_from("<I",after,8)[0],zlib.adler32(after[12:]) & 0xffffffff)
        self.assertTrue(report["sha1_recomputed"])
        self.assertTrue(report["adler32_recomputed"])

    def test_rejects_missing_literal(self):
        with self.assertRaises(ValueError):
            patch_dex(self.synthetic_dex(b"no-app-id-here"))

    def test_rejects_non_dex(self):
        with self.assertRaises(ValueError):
            patch_dex(b"not-a-dex" + bytes(160))

if __name__ == "__main__":
    unittest.main()
