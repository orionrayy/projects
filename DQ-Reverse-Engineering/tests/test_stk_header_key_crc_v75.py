from __future__ import annotations
import copy,json,pathlib,sys,unittest,zlib,struct
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from patch_stk_header_key_crc_v75 import HEADER,ENTRY,StkFixError,parse_stk,repair_stk,decode_payload
from validate_stk_header_key_crc_apk_v75 import AuditError,validate as validate_report
REPORT=ROOT/"docs"/"STK_HEADER_KEY_CRC_FIX_V75.json"
def xor_bytes(data,key):
 kb=struct.pack("<I",key)
 return bytes(v^kb[i&3] for i,v in enumerate(data))
def make_stk(items,header_key_override=None):
 stored_map={};entries=[]
 for name,decoded,alias in items:
  blob=zlib.compress(decoded,9); token=alias if alias is not None else ("unique",name)
  if token not in stored_map:stored_map[token]=(len(stored_map) and 0 or 0,blob)
  entries.append((name,decoded,token,blob))
 # Assign offsets from unique token order, creating exact aliases where tokens repeat.
 payload=bytearray();positions={}
 for name,decoded,token,blob in entries:
  if token not in positions:
   positions[token]=(len(payload),blob);payload.extend(b"\0"*len(blob))
 for name,decoded,token,blob in entries:
  off,actual=positions[token]
  if actual!=blob:raise AssertionError("aliased payload bytes differ")
  payload[off:off+len(blob)]=xor_bytes(blob,0x12345678)
 rows=[]
 for name,decoded,token,blob in entries:
  off,_=positions[token];rows.append({"name":name,"offset":off,"csize":len(blob),"usize":len(decoded),"crc":zlib.crc32(blob)&0xffffffff,"flags":4})
 table=bytearray()
 for e in rows:
  n=e["name"].encode();table.extend(len(n).to_bytes(4,"little"));table.extend(n)
  table.extend(ENTRY.pack(e["offset"],e["csize"],e["usize"],e["crc"],e["flags"]))
 good=zlib.crc32(table)&0xffffffff;key=good if header_key_override is None else header_key_override
 # Re-encode referenced ranges to key so a key-mismatch fixture remains parseable.
 for token,(off,blob) in positions.items():payload[off:off+len(blob)]=xor_bytes(blob,key)
 return HEADER.pack(6,8,b"12345678",key,len(rows),HEADER.size+len(table))+xor_bytes(bytes(table),key)+bytes(payload)
class PatcherTests(unittest.TestCase):
 def setUp(self):
  self.source=make_stk([("a.bin",b"alpha"*30,"shared"),("b.bin",b"alpha"*30,"shared"),("Resources/HUD/pause.hud",b"stock pause hud v1",None),("tail.bin",b"other payload"*20,None)])
  self.candidate=make_stk([("a.bin",b"alpha"*30,None),("b.bin",b"alpha"*30,None),("Resources/HUD/pause.hud",b"modified pause hud v2 with more text",None),("tail.bin",b"other payload"*20,None)],header_key_override=0x12345678)
 def test_repair_sets_header_key_crc_and_changes_only_target(self):
  out,r=repair_stk(self.source,self.candidate);src=parse_stk(self.source);fixed=parse_stk(out);cand=parse_stk(self.candidate)
  self.assertEqual(fixed["key"],fixed["table_crc"])
  self.assertEqual(r["changed_decoded_entries"],["Resources/HUD/pause.hud"])
  self.assertEqual(r["unchanged_decoded_entries_identical"],3)
  self.assertEqual(r["non_target_entry_offsets_preserved"],3)
  self.assertEqual(r["output_non_target_exact_alias_groups"],1)
  by={e["name"]:e for e in fixed["entries"]};cb={e["name"]:e for e in cand["entries"]}
  self.assertEqual(by["Resources/HUD/pause.hud"]["offset"],src["payload_size"])
  self.assertEqual([e["offset"] for e in src["entries"] if e["name"]!="Resources/HUD/pause.hud"],[e["offset"] for e in fixed["entries"] if e["name"]!="Resources/HUD/pause.hud"])
  self.assertEqual(decode_payload(fixed,by["Resources/HUD/pause.hud"]),decode_payload(cand,cb["Resources/HUD/pause.hud"]))
 def test_source_must_be_known_good_control(self):
  bad=make_stk([("a.bin",b"abc",None),("Resources/HUD/pause.hud",b"old",None)],header_key_override=0x12345678)
  with self.assertRaisesRegex(StkFixError,"source archive does not satisfy"):repair_stk(bad,self.candidate,"Resources/HUD/pause.hud")
 def test_target_shared_payload_is_rejected(self):
  src=make_stk([("Resources/HUD/pause.hud",b"old","shared"),("alias.bin",b"old","shared")])
  cand=make_stk([("Resources/HUD/pause.hud",b"new",None),("alias.bin",b"old",None)])
  with self.assertRaisesRegex(StkFixError,"target source payload is aliased"):repair_stk(src,cand,"Resources/HUD/pause.hud")
 def test_target_flags_must_match(self):
  src=make_stk([("a.bin",b"abc",None),("Resources/HUD/pause.hud",b"old",None)])
  cand=make_stk([("a.bin",b"abc",None),("Resources/HUD/pause.hud",b"new",None)])
  p=parse_stk(cand);es=[dict(e) for e in p["entries"]]
  for e in es:
   if e["name"]=="Resources/HUD/pause.hud":e["flags"]=3
  table=bytearray()
  for e in es:
   n=e["name"].encode();table.extend(len(n).to_bytes(4,"little"));table.extend(n);table.extend(ENTRY.pack(e["offset"],e["csize"],e["usize"],e["crc"],e["flags"]))
  key=zlib.crc32(table)&0xffffffff;payload=bytearray(p["payload"]);groups={}
  for e in es:groups.setdefault((e["offset"],e["csize"]),e)
  for (off,size),e in groups.items():
   plain=xor_bytes(p["payload"][off:off+size],p["key"]);payload[off:off+size]=xor_bytes(plain,key)
  bad=HEADER.pack(p["raw_flags"],p["signature"],p["padding"],key,p["count"],p["table_end"])+xor_bytes(bytes(table),key)+bytes(payload)
  with self.assertRaisesRegex(StkFixError,"target flags changed"):repair_stk(src,bad)
 def test_real_apk_report_is_fail_closed(self):
  d=json.loads(REPORT.read_text(encoding="utf-8"));r=validate_report(copy.deepcopy(d))
  self.assertEqual(r["status"],"PASS_STATIC_V75_STK_CRC_KEY_FIX")
  d["stk"]["header_key_equals_metadata_crc"]=False
  with self.assertRaisesRegex(AuditError,"invariant not proven"):validate_report(d)
if __name__=="__main__":unittest.main(verbosity=2)
