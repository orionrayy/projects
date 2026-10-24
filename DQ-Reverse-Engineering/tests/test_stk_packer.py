import pathlib, struct, tempfile, unittest, zlib, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from stk_packer import HEADER, ENTRY_META, SIGNATURE, StkArchive, xor_bytes, safe_path

def make_pack(items):
    key=0x4c4060e8
    payloads=[]
    for name, plain in items:
        compressed=zlib.compress(plain,9)
        stored=plain if len(compressed)>=len(plain) else compressed
        payloads.append((name,stored,len(plain)))
    table=bytearray(); offset=0
    for name, stored, usize in payloads:
        nb=name.encode()
        table.extend(struct.pack("<I",len(nb))); table.extend(nb)
        table.extend(ENTRY_META.pack(offset,len(stored),usize,zlib.crc32(stored)&0xffffffff,0))
        offset+=len(stored)
    end=HEADER.size+len(table)
    out=bytearray(HEADER.pack(6,SIGNATURE,b"\0"*8,key,len(payloads),end))
    out.extend(xor_bytes(bytes(table),key))
    for _,stored,_ in payloads: out.extend(xor_bytes(stored,key))
    return bytes(out)

class PackerTests(unittest.TestCase):
    def test_roundtrip_and_replace_one_entry(self):
        src=StkArchive(make_pack([("a.txt",b"hello "*20),("b.bin",bytes(range(64)))]))
        rebuilt=StkArchive(src.rebuild({"a.txt":b"changed value"}))
        self.assertEqual(rebuilt.decode(rebuilt.entries[0]),b"changed value")
        self.assertEqual(rebuilt.decode(rebuilt.entries[1]),bytes(range(64)))
    def test_noop_preserves_decoded_contents(self):
        src=StkArchive(make_pack([("a",b"A"*100),("b",b"123456")]))
        out=StkArchive(src.rebuild({}))
        self.assertEqual([out.decode(e) for e in out.entries],[src.decode(e) for e in src.entries])
    def test_missing_target_rejected(self):
        with self.assertRaisesRegex(ValueError,"not found"):
            StkArchive(make_pack([("a",b"abc")])).rebuild({"nope":b"x"})
    def test_traversal_rejected(self):
        with self.assertRaises(ValueError): safe_path("../escape")
        with self.assertRaises(ValueError): safe_path("/absolute")
    def test_crc_corruption_rejected(self):
        raw=bytearray(make_pack([("a",b"A"*100)])); raw[-1]^=1
        with self.assertRaises(ValueError): StkArchive(bytes(raw)).decode(StkArchive(bytes(raw)).entries[0])
    def test_duplicate_casefold_rejected(self):
        with self.assertRaises(ValueError): StkArchive(make_pack([("A",b"a"),("a",b"b")]))
if __name__ == "__main__": unittest.main()
