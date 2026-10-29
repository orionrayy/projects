from __future__ import annotations
import json,pathlib,struct,tempfile,unittest,sys
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent.parent/"tools"))
import audit_first50_target_effects_v86 as audit

def make_registry(ids=None):
 ids=list(ids) if ids is not None else list(audit.ROUTES)+[f"test.extra_{i:02d}" for i in range(39)]
 return {"schema":"test","fully_integrated":0,"cheats":[{"id":x,"runtime_verified":False} for x in ids]}
def make_hud(actions):
 blob=bytearray(struct.pack("<H",len(actions)))
 def st(v):
  b=v.encode();return struct.pack("<I",len(b))+b
 for name,statements in actions.items():
  blob.extend(st(name));blob.extend(struct.pack("<H",len(statements)))
  for statement in statements:
   b=statement.encode();blob.extend(struct.pack("<I",len(b)));blob.extend(b)
  blob.extend(struct.pack("<I",0))
 out=bytearray(struct.pack("<I",3)+b"NcP"+bytes([12]))
 for section in (b"\0\0\0\0",b"\0\0\0\0",bytes(blob),b"\0\0"):
  out.extend(struct.pack("<I",len(section)));out.extend(section)
 return bytes(out)
def make_elf(symbols):
 names=b"\0";offsets={}
 for name in symbols:offsets[name]=len(names);names+=name.encode()+b"\0"
 sym=bytearray(b"\0"*24)
 for name,(va,size) in symbols.items():sym.extend(struct.pack("<IBBHQQ",offsets[name],0x12,0,1,va,size))
 out=bytearray(b"\0"*64);shstr=b"\0.shstrtab\0.dynstr\0.dynsym\0"
 shstr_off=len(out);out.extend(shstr);dynstr_off=len(out);out.extend(names);sym_off=len(out);out.extend(sym);shoff=len(out)
 def sec(name,typ,off,size,link=0,entsize=0):
  no=shstr.find(name.encode()+b"\0");return struct.pack("<IIQQQQIIQQ",no,typ,0,0,off,size,link,0,1,entsize)
 out.extend(b"\0"*64);out.extend(sec(".shstrtab",3,shstr_off,len(shstr)));out.extend(sec(".dynstr",3,dynstr_off,len(names)));out.extend(sec(".dynsym",11,sym_off,len(sym),2,24))
 ident=b"\x7fELF"+bytes([2,1,1])+b"\0"*9
 out[:64]=struct.pack("<16sHHIQQQIHHHHHH",ident,3,183,1,0,0,shoff,0,64,0,0,64,4,1)
 return bytes(out)

class AuditV86Tests(unittest.TestCase):
 def test_catalog_50_unique_does_not_promote_runtime(self):
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/"catalog.json";p.write_text(json.dumps(make_registry()));r=audit.audit(p,None,None)
  self.assertEqual((r["catalog"]["items"],r["catalog"]["unique_ids"]),(50,50))
  self.assertEqual(r["verification_limits"]["gameplay_effects_verified"],0)
  self.assertEqual(r["status"],"STATIC_SOURCE_EVIDENCE_ONLY_RUNTIME_NOT_VERIFIED")
 def test_catalog_rejects_duplicates(self):
  ids=list(audit.ROUTES)+[f"test.extra_{i:02d}" for i in range(39)];ids[-1]=ids[0]
  with tempfile.TemporaryDirectory() as td:
   p=pathlib.Path(td)/"catalog.json";p.write_text(json.dumps(make_registry(ids)))
   with self.assertRaisesRegex(audit.AuditError,"unique nonempty IDs"):audit.audit(p,None,None)
 def test_action_parser_reads_call_literals(self):
  actions={name:[f"<023><8,3>013<2,10>uai_gp_hud<2,7>onDebug<1,5>{n:.3f}"] for _,(name,n) in audit.ROUTES.items()}
  parsed=audit.parse_hud_actions(make_hud(actions),"fixture.hud")
  self.assertEqual(parsed,actions)
 def test_action_parser_rejects_trailing_bytes(self):
  with self.assertRaisesRegex(audit.AuditError,"trailing bytes"):audit.parse_hud_actions(make_hud({"onClose":["noop"]})+b"x","bad.hud")
 def test_elf_parser_reads_aarch64_symbols(self):
  name="_ZN10uai_gp_hud7onDebugEiPKN4S3DX10AIVariableEPS1_"
  self.assertEqual(audit.elf64_symbols(make_elf({name:(0x6D5048,0x169C)}))[name][:2],(0x6D5048,0x169C))
 def test_elf_parser_rejects_non_elf(self):
  with self.assertRaisesRegex(audit.AuditError,"ELF64"):audit.elf64_symbols(b"not ELF")
if __name__=="__main__":unittest.main(verbosity=2)
