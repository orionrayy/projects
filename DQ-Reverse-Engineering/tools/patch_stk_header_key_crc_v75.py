#!/usr/bin/env python3
"""Repair a v6 STK header-key/metadata-CRC invariant without rewriting unrelated payloads."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, struct, zlib
from typing import Any
HEADER=struct.Struct("<BI8sIII")
ENTRY=struct.Struct("<IIIIH")
STK_SIGNATURE=0x00000008
MAX_ENTRIES=100_000
MAX_NAME_BYTES=2048
MAX_ENTRY_SIZE=512*1024*1024
SCHEMA="dq-stk-header-key-crc-fix-v75"
class StkFixError(ValueError): pass
def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def xor_bytes(data:bytes,key:int)->bytes:
 kb=struct.pack("<I",key)
 return bytes(v^kb[i&3] for i,v in enumerate(data))
def safe_name(value:str)->str:
 value=value.replace("\\","/")
 p=pathlib.PurePosixPath(value)
 if not value or p.is_absolute() or "\x00" in value or any(x in ("",".","..") for x in p.parts) or (p.parts and ":" in p.parts[0]):
  raise StkFixError("unsafe STK entry path: "+repr(value))
 return p.as_posix()
def parse_stk(data:bytes,label:str="<memory>")->dict[str,Any]:
 if len(data)<HEADER.size: raise StkFixError(label+": STK header truncated")
 raw,sig,pad,key,count,end=HEADER.unpack_from(data)
 if sig!=STK_SIGNATURE or raw&0x0f!=6: raise StkFixError(label+": expected STK version 6")
 if raw&0x30: raise StkFixError(label+": unsupported compression flag bits")
 if count<1 or count>MAX_ENTRIES: raise StkFixError(label+": unreasonable entry count")
 if not HEADER.size<=end<=len(data): raise StkFixError(label+": metadata end outside file")
 table=xor_bytes(data[HEADER.size:end],key); pos=0; entries=[]; seen=set()
 for idx in range(count):
  if pos+4>len(table): raise StkFixError(label+": truncated entry name length")
  ns=struct.unpack_from("<I",table,pos)[0];pos+=4
  if ns<1 or ns>MAX_NAME_BYTES or pos+ns+ENTRY.size>len(table): raise StkFixError(label+": invalid entry name size")
  try: name=safe_name(table[pos:pos+ns].decode("utf-8"))
  except UnicodeError as exc: raise StkFixError(label+": invalid UTF-8 entry name") from exc
  pos+=ns
  off,cs,us,crc,flags=ENTRY.unpack_from(table,pos);pos+=ENTRY.size
  if name.casefold() in seen: raise StkFixError(label+": duplicate/case-colliding entry "+name)
  seen.add(name.casefold())
  if us>MAX_ENTRY_SIZE: raise StkFixError(label+": unreasonable decoded size "+name)
  entries.append({"name":name,"offset":off,"csize":cs,"usize":us,"crc":crc,"flags":flags})
 if pos!=len(table): raise StkFixError(label+": metadata trailing bytes")
 payload=data[end:]
 for e in entries:
  if e["offset"]>len(payload) or e["csize"]>len(payload)-e["offset"]:
   raise StkFixError(label+": payload range out of bounds "+e["name"])
 return {"data":data,"raw_flags":raw,"signature":sig,"padding":pad,"key":key,"count":count,"table_end":end,
         "table":table,"table_crc":zlib.crc32(table)&0xffffffff,"entries":entries,"payload":payload,
         "payload_size":len(payload),"label":label}
def range_groups(parsed:dict[str,Any])->dict[tuple[int,int],list[dict[str,Any]]]:
 groups={}
 for e in parsed["entries"]: groups.setdefault((e["offset"],e["csize"]),[]).append(e)
 prev_end=-1; prev=None
 for off,size in sorted(groups):
  if prev is not None and off<prev_end: raise StkFixError(parsed["label"]+": partial payload overlap "+repr(prev)+" vs "+repr((off,size)))
  prev=(off,size);prev_end=off+size
 return groups
def stored_payload(parsed:dict[str,Any],e:dict[str,Any])->bytes:
 raw=xor_bytes(parsed["payload"][e["offset"]:e["offset"]+e["csize"]],parsed["key"])
 if zlib.crc32(raw)&0xffffffff!=e["crc"]: raise StkFixError(parsed["label"]+": stored CRC mismatch "+e["name"])
 return raw
def decode_payload(parsed:dict[str,Any],e:dict[str,Any])->bytes:
 raw=stored_payload(parsed,e)
 if e["csize"]==e["usize"]: out=raw
 else:
  try:
   dec=zlib.decompressobj();out=dec.decompress(raw)+dec.flush()
  except zlib.error as exc: raise StkFixError(parsed["label"]+": zlib decode failed "+e["name"]) from exc
  if not dec.eof or dec.unused_data or dec.unconsumed_tail: raise StkFixError(parsed["label"]+": invalid/trailing zlib data "+e["name"])
 if len(out)!=e["usize"]: raise StkFixError(parsed["label"]+": decoded-size mismatch "+e["name"])
 return out
def build_table(entries:list[dict[str,Any]])->bytes:
 b=bytearray()
 for e in entries:
  name=safe_name(e["name"]).encode("utf-8")
  b.extend(struct.pack("<I",len(name)));b.extend(name)
  b.extend(ENTRY.pack(e["offset"],e["csize"],e["usize"],e["crc"],e["flags"]))
 return bytes(b)
def repair_stk(source_data:bytes,candidate_data:bytes,target_name:str="Resources/HUD/pause.hud")->tuple[bytes,dict[str,Any]]:
 target_name=safe_name(target_name)
 source=parse_stk(source_data,"source");candidate=parse_stk(candidate_data,"candidate")
 if source["key"]!=source["table_crc"]: raise StkFixError("source archive does not satisfy header-key == metadata-table CRC; use known-good stock")
 groups=range_groups(source);range_groups(candidate)
 sb={e["name"]:e for e in source["entries"]};cb={e["name"]:e for e in candidate["entries"]}
 if sb.keys()!=cb.keys(): raise StkFixError("source/candidate inventories differ")
 if target_name not in sb: raise StkFixError("target absent: "+target_name)
 old,new=sb[target_name],cb[target_name]
 if len(groups[(old["offset"],old["csize"])])!=1: raise StkFixError("target source payload is aliased; refusing to detach a shared range")
 if old["flags"]!=new["flags"]: raise StkFixError("target flags changed between source and candidate")
 replacement=stored_payload(candidate,new); decoded_replacement=decode_payload(candidate,new)
 entries=[]
 for src in source["entries"]:
  e=dict(src)
  if src["name"]==target_name:
   e.update(offset=source["payload_size"],csize=len(replacement),usize=len(decoded_replacement),crc=zlib.crc32(replacement)&0xffffffff)
  entries.append(e)
 table=build_table(entries)
 if len(table)!=len(source["table"]): raise StkFixError("metadata table size changed")
 newkey=zlib.crc32(table)&0xffffffff
 if newkey==source["key"]: raise StkFixError("modified table unexpectedly kept old key")
 payload=bytearray(source["payload"])
 for (off,size),aliases in groups.items():
  raw=xor_bytes(source["payload"][off:off+size],source["key"])
  crc=zlib.crc32(raw)&0xffffffff
  if any(e["crc"]!=crc for e in aliases): raise StkFixError("alias CRC disagreement at "+repr((off,size)))
  payload[off:off+size]=xor_bytes(raw,newkey)
 target_new_offset=len(payload);payload.extend(xor_bytes(replacement,newkey))
 header=HEADER.pack(source["raw_flags"],source["signature"],source["padding"],newkey,source["count"],source["table_end"])
 output=header+xor_bytes(table,newkey)+bytes(payload)
 checked=parse_stk(output,"repaired")
 if checked["key"]!=checked["table_crc"]: raise StkFixError("header-key/metadata-CRC invariant failed")
 checked_groups=range_groups(checked); checked_by={e["name"]:e for e in checked["entries"]}
 changed=[];unchanged=0;offsets=0
 for olde in source["entries"]:
  newe=checked_by[olde["name"]];got=decode_payload(checked,newe)
  if olde["name"]==target_name:
   if got!=decoded_replacement: raise StkFixError("target payload mismatch")
   changed.append(olde["name"])
  else:
   if decode_payload(source,olde)!=got: raise StkFixError("non-target decoded payload changed: "+olde["name"])
   if any(olde[k]!=newe[k] for k in ("offset","csize","usize","crc","flags")): raise StkFixError("non-target metadata changed: "+olde["name"])
   unchanged+=1;offsets+=1
 src_alias=sorted(sorted(e["name"] for e in g) for g in groups.values() if len(g)>1)
 out_alias=sorted(sorted(e["name"] for e in g) for g in checked_groups.values() if len(g)>1 and all(e["name"]!=target_name for e in g))
 if src_alias!=out_alias: raise StkFixError("non-target exact-alias topology changed")
 report={"schema":SCHEMA,"status":"PASS_STK_METADATA_KEY_AND_ENTRY_VALIDATION",
  "source_sha256":sha256(source_data),"source_size_bytes":len(source_data),"candidate_sha256":sha256(candidate_data),"candidate_size_bytes":len(candidate_data),
  "source_header_key_hex":f"0x{source['key']:08x}","source_metadata_crc32_hex":f"0x{source['table_crc']:08x}",
  "candidate_header_key_hex":f"0x{candidate['key']:08x}","candidate_metadata_crc32_hex":f"0x{candidate['table_crc']:08x}",
  "output_sha256":sha256(output),"output_size_bytes":len(output),"output_header_key_hex":f"0x{checked['key']:08x}",
  "output_metadata_crc32_hex":f"0x{checked['table_crc']:08x}","header_key_equals_metadata_crc":checked["key"]==checked["table_crc"],
  "entry_count":checked["count"],"verified_entry_count":checked["count"],"changed_decoded_entries":changed,
  "unchanged_decoded_entries_identical":unchanged,"non_target_entry_offsets_preserved":offsets,
  "source_exact_alias_groups":len(src_alias),"output_non_target_exact_alias_groups":len(out_alias),
  "all_non_target_exact_alias_topology_preserved":True,"target_old_offset":old["offset"],"target_new_offset":target_new_offset,
  "target_old_csize":old["csize"],"target_new_csize":len(replacement),"target_old_usize":old["usize"],
  "target_new_usize":len(decoded_replacement),"source_artifacts_overwritten":False}
 return output,report
def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("source_stock_stk",type=pathlib.Path);p.add_argument("candidate_stk",type=pathlib.Path);p.add_argument("output_stk",type=pathlib.Path);p.add_argument("--target",default="Resources/HUD/pause.hud");p.add_argument("--report",type=pathlib.Path);a=p.parse_args()
 try:
  src,cand,out=(x.resolve() for x in (a.source_stock_stk,a.candidate_stk,a.output_stk))
  if len({src,cand,out})!=3: raise StkFixError("source, candidate and output must differ")
  if out.exists() or out.is_symlink(): raise StkFixError("refusing to overwrite output")
  if a.report and a.report.exists(): raise StkFixError("refusing to overwrite report")
  payload,r=repair_stk(src.read_bytes(),cand.read_bytes(),a.target);out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(payload)
  if a.report: a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(json.dumps(r,indent=2)+"\n",encoding="utf-8")
  print(json.dumps(r,indent=2));return 0
 except (OSError,ValueError,struct.error,zlib.error,UnicodeError) as exc:
  print(json.dumps({"status":"FAIL","error":str(exc)},indent=2));return 2
if __name__=="__main__": raise SystemExit(main())
