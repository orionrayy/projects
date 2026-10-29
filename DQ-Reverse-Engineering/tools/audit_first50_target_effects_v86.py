#!/usr/bin/env python3
"""Read-only exact-build audit for the canonical first-50 Dungeon Quest catalog."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, struct, sys
from typing import Any

SCHEMA = "dq-first50-target-effect-audit-v86"
STOCK_NATIVE_SHA256 = "0424bd9c24d244847149fd89b5cca596629e7a06f62cdf68a3c5bdd996239083"
PINNED_ASSETS = {
 "AIModels/uai_gp_hud.aim":"66607a46a23eeaab4fa2dac02772adbea5ab71e65d4e446e49396c6af6a451cb",
 "HUD/debug.hud":"02ed5420fceacaba5bc614596fddc52646abf04914446e26bc240806930f15b6",
 "HUD/pause.hud":"12499b08c49b4a5bb34649468b910b62ba1a64adfd831bd638d13d420af9f395",
}
ROUTES = {
 "progression.player_level":("onSetLevel",4.0),
 "progression.floor_target":("onGotoLevel",2.0),
 "progression.add_levels":("onAddLevel",11.0),
 "inventory.grant_legend_fixture":("onCreateLegend",8.0),
 "inventory.grant_mythstone_fixture":("onCreateMS",9.0),
 "inventory.grant_character_stone_fixture":("onCreateCS",10.0),
 "inventory.grant_feat_fixture":("onCreateFeat",13.0),
 "rewards.add_battle":("onAddBattle",16.0),
 "rewards.add_heroic":("onAddHeroic",12.0),
 "rewards.add_crystal":("onSetCrystal",14.0),
 "rewards.add_eternal":("onSetEternal",15.0),
}
SYMBOLS = {
 "_ZN10uai_gp_hud7onDebugEiPKN4S3DX10AIVariableEPS1_":(0x6D5048,0x169C),
 "_ZN10uai_gp_hud10RewardGoldEN4S3DX10AIVariableE":(0x65FEEC,0x644),
 "_ZN10uai_gp_hud10RewardDustEN4S3DX10AIVariableE":(0x65EEEC,0x38C),
 "_ZN10uai_gp_hud10onSetLevelEiPKN4S3DX10AIVariableEPS1_":(0x7506A4,0xE8),
 "_ZN10uai_gp_hud9onSetGoldEiPKN4S3DX10AIVariableEPS1_":(0x74FF84,0x120),
 "_ZN10uai_gp_hud11onSetHealthEiPKN4S3DX10AIVariableEPS1_":(0x7500A4,0x200),
 "_ZN10uai_gp_hud9onSetManaEiPKN4S3DX10AIVariableEPS1_":(0x75090C,0x200),
}
GOLD_CALL_OFFSET=0x6D5A64
GOLD_CALL_BYTES=bytes.fromhex("2229fe97")

class AuditError(ValueError): pass
def sha256(data:bytes)->str: return hashlib.sha256(data).hexdigest()
def u32(data:bytes,pos:int)->int:
 if pos<0 or pos+4>len(data): raise AuditError(f"u32 out of bounds at 0x{pos:x}")
 return struct.unpack_from("<I",data,pos)[0]

def parse_hud_actions(data:bytes,source:str)->dict[str,list[str]]:
 if len(data)<8 or u32(data,0)!=3 or data[4:7] not in (b"NcP",b"NcX",b"NcI") or data[7]!=12:
  raise AuditError(f"{source}: expected version-12 HUD")
 pos=8; sections={}
 for name in ("general","elements","actions","timers"):
  size=u32(data,pos);pos+=4
  if pos+size>len(data):raise AuditError(f"{source}: truncated {name}")
  sections[name]=data[pos:pos+size];pos+=size
 if pos!=len(data):raise AuditError(f"{source}: trailing bytes")
 blob=sections["actions"];pos=0
 def take(n):
  nonlocal pos
  if n<0 or pos+n>len(blob):raise AuditError(f"{source}: truncated action table")
  out=blob[pos:pos+n];pos+=n;return out
 def r16():return struct.unpack("<H",take(2))[0]
 def r32():return struct.unpack("<I",take(4))[0]
 def string():
  n=r32()
  if n>2_000_000:raise AuditError(f"{source}: unreasonable string size")
  return take(n).decode("utf-8",errors="surrogateescape")
 count=r16();actions={}
 for _ in range(count):
  name=string();nstat=r16();stmts=[]
  if nstat>100_000:raise AuditError(f"{source}: unreasonable statement count")
  for __ in range(nstat):
   size=r32()
   if not size or size>2_000_000:raise AuditError(f"{source}: invalid statement size {size}")
   stmts.append(take(size).decode("utf-8",errors="surrogateescape"))
  if r32()!=0:raise AuditError(f"{source}: invalid terminator in {name}")
  if name in actions:raise AuditError(f"{source}: duplicate action {name}")
  actions[name]=stmts
 if pos!=len(blob):raise AuditError(f"{source}: trailing action bytes")
 return actions

def elf64_symbols(data:bytes)->dict[str,tuple[int,int,int]]:
 if len(data)<64 or data[:4]!=b"\x7fELF" or data[4]!=2 or data[5]!=1:raise AuditError("native library must be ELF64 little-endian")
 h=struct.unpack_from("<16sHHIQQQIHHHHHH",data,0)
 machine,shoff,shstride,shnum=h[2],h[6],h[11],h[12]
 if machine!=183:raise AuditError(f"ELF machine {machine}; expected AArch64 (183)")
 if shstride<64 or shoff+shstride*shnum>len(data):raise AuditError("invalid ELF section table")
 sections=[struct.unpack_from("<IIQQQQIIQQ",data,shoff+i*shstride) for i in range(shnum)]
 symbols={}
 for sec in sections:
  _,typ,_,_,off,size,link,_,_,entsize=sec
  if typ not in (2,11):continue
  if link>=len(sections):raise AuditError("invalid ELF string table link")
  st=sections[link];so,ss=st[4],st[5]
  if so+ss>len(data):raise AuditError("invalid ELF string table")
  strings=data[so:so+ss];stride=entsize or 24
  if stride<24 or off+size>len(data) or size%stride:raise AuditError("invalid ELF symbol table")
  for p in range(off,off+size,stride):
   no,info,other,shndx,value,sz=struct.unpack_from("<IBBHQQ",data,p)
   if no>=len(strings):continue
   end=strings.find(b"\0",no)
   if end>=0:
    name=strings[no:end].decode("utf-8",errors="replace")
    if name:symbols[name]=(value,sz,info)
 return symbols

def audit(registry_path:pathlib.Path,assets_root:pathlib.Path|None,native_path:pathlib.Path|None)->dict[str,Any]:
 registry=json.loads(registry_path.read_text(encoding="utf-8"));cheats=registry.get("cheats",[])
 ids=[x.get("id") for x in cheats]
 if len(cheats)!=50 or any(not isinstance(x,str) or not x for x in ids) or len(set(ids))!=50:
  raise AuditError(f"catalog must have exactly 50 unique nonempty IDs; got {len(cheats)} items/{len(set(ids))} unique")
 by_id={x["id"]:x for x in cheats}
 for cid in ROUTES:
  if cid not in by_id:raise AuditError(f"route refers to unknown catalog ID {cid}")
 out={"schema":SCHEMA,"status":"STATIC_SOURCE_EVIDENCE_ONLY_RUNTIME_NOT_VERIFIED",
  "catalog":{"path":registry_path.name,"items":50,"unique_ids":50,
   "runtime_verified":sum(bool(x.get("runtime_verified")) for x in cheats),"fully_integrated":registry.get("fully_integrated",0)},
  "stock_asset_hashes":{},"debug_hud":None,"native_library":None,"routes":[],
  "verification_limits":{"gameplay_effects_verified":0,"save_reload_verified":0,"rollback_verified":0,"apk_built":False,"device_tested":False,
   "reason":"Static symbols and HUD calls do not prove gameplay effects, authoritative read-back, persistence, or recovery."}}
 if assets_root is not None:
  for rel,expected in PINNED_ASSETS.items():
   path=assets_root/rel
   if not path.is_file():raise AuditError(f"missing source asset {path}")
   actual=sha256(path.read_bytes());out["stock_asset_hashes"][rel]={"sha256":actual,"expected":expected,"match":actual==expected}
   if actual!=expected:raise AuditError(f"source hash mismatch {rel}: {actual}")
  hud=(assets_root/"HUD/debug.hud").read_bytes();actions=parse_hud_actions(hud,"debug.hud")
  for cid,(action,number) in ROUTES.items():
   target="<2,10>uai_gp_hud<2,7>onDebug<1,"
   hits=[x for x in actions.get(action,[]) if target in x and x.endswith(f">{number:.3f}")]
   if len(hits)!=1:raise AuditError(f"debug.hud route mismatch for {cid}: {action} expected {number}")
   out["routes"].append({"id":cid,"hud_action":action,"callback":"uai_gp_hud.onDebug","argument":number,
    "source_call_present":True,"effect_verified":False,"save_reload_verified":False,"rollback_verified":False})
  out["debug_hud"]={"sha256":sha256(hud),"action_count":len(actions),"on_debug_routes":len(out["routes"]),"contract":"static_callsite_only"}
 if native_path is not None:
  native=native_path.read_bytes();nh=sha256(native)
  if nh!=STOCK_NATIVE_SHA256:raise AuditError(f"native SHA mismatch: {nh}")
  syms=elf64_symbols(native);items={}
  for name,(va,size) in SYMBOLS.items():
   got=syms.get(name)
   if got is None or got[:2]!=(va,size):raise AuditError(f"native symbol mismatch {name}: {got}")
   items[name]={"va":hex(va),"size":size,"present":True,"semantics_proven":False}
  call=native[GOLD_CALL_OFFSET:GOLD_CALL_OFFSET+4]
  if call!=GOLD_CALL_BYTES:raise AuditError(f"RewardGold instruction mismatch: {call.hex()}")
  if native[0xCC973F:0xCC973F+10]!=b"hud.level\0":raise AuditError("onSetLevel HUD key literal mismatch")
  out["native_library"]={"sha256":nh,"machine":"AArch64","symbol_table_verified":True,"symbols":items,
   "reward_gold_fixed_call":{"file_offset":hex(GOLD_CALL_OFFSET),"instruction_le_hex":call.hex(),"command_case":6.0,
    "direct_target":"uai_gp_hud::RewardGold(S3DX::AIVariable)","semantics":"fixed +100000 Gold; not an arbitrary amount setter","runtime_verified":False},
   "on_set_level":{"key_literal_va":"0xcc973f","key_literal":"hud.level","interpretation":"HUD variable; authoritative player-level mutation not proven","runtime_verified":False}}
 return out

def main()->int:
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--registry",type=pathlib.Path,required=True)
 p.add_argument("--assets-root",type=pathlib.Path);p.add_argument("--native-lib",type=pathlib.Path);p.add_argument("--report",type=pathlib.Path)
 a=p.parse_args()
 try:
  out=json.dumps(audit(a.registry,a.assets_root,a.native_lib),indent=2,ensure_ascii=False)+"\n"
  if a.report:
   if a.report.exists():raise AuditError(f"refusing to overwrite report: {a.report}")
   a.report.parent.mkdir(parents=True,exist_ok=True);a.report.write_text(out,encoding="utf-8")
  print(out,end="");return 0
 except (OSError,ValueError,struct.error,json.JSONDecodeError) as e:
  print(json.dumps({"schema":SCHEMA,"status":"FAIL","error":str(e)},ensure_ascii=False),file=sys.stderr);return 2
if __name__=="__main__":raise SystemExit(main())
