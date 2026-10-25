#!/usr/bin/env python3
"""Read-only, fail-closed audit of the actual Dungeon Quest stock/v50 APK packages.

This validates package identity, XAPK split inventory, decoded APK payload differences,
pinned classes.dex identity, native-library parity and the full decoded STK delta.
It never modifies the APK inputs and does not claim install or runtime validity.
"""
from __future__ import annotations
import argparse, hashlib, io, json, pathlib, sys, zipfile
from typing import Any

ROOT=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT))
from stk_packer import StkArchive
from dq_install_preflight_v56 import decode_manifest_identity

STOCK_SHA="3035e3fcb1d5325ac844323208815c654af96074438c0d93f819f79453e6597b"
CAND_XAPK_SHA="680dd37d23c6ea6ee318e5d08c82dca7cee8bb82e6a8baae75ed7912710c6430"
CAND_APK_SHA="f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa"
DEX_SHA="bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
EXPECTED_STK_PATH="Resources/HUD/pause.hud"
BASE_SPLIT="com.shinybox.smash.apk"

class AuditError(ValueError): pass

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def is_signing_metadata(name: str) -> bool:
    upper=name.upper()
    if not upper.startswith("META-INF/"): return False
    leaf=upper.rsplit("/",1)[-1]
    return leaf=="MANIFEST.MF" or leaf.endswith((".SF",".RSA",".DSA",".EC")) or leaf.startswith("SIG-")

def payload_hashes(z: zipfile.ZipFile) -> dict[str,str]:
    names=z.namelist()
    if len(names)!=len(set(names)): raise AuditError("APK contains duplicate ZIP paths")
    return {n:sha(z.read(n)) for n in names if not n.endswith("/") and not is_signing_metadata(n)}

def changed_payload_paths(left: dict[str,str], right: dict[str,str]) -> list[str]:
    return [name for name in sorted(set(left)|set(right)) if left.get(name)!=right.get(name)]

def inspect_apk_bytes(raw: bytes, name: str) -> dict[str,Any]:
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            bad=z.testzip()
            if bad: raise AuditError(f"{name}: APK CRC failure at {bad}")
            if "AndroidManifest.xml" not in z.namelist(): raise AuditError(f"{name}: manifest missing")
            identity=decode_manifest_identity(z.read("AndroidManifest.xml"))
            result={"name":name,"bytes":len(raw),"sha256":sha(raw),"entry_count":len(z.namelist()),
                    "zip_crc":"PASS",**identity,"payload_hashes":payload_hashes(z),
                    "classes_dex_sha256":sha(z.read("classes.dex")) if "classes.dex" in z.namelist() else None,
                    "native_hashes":{n:sha(z.read(n)) for n in z.namelist() if n.startswith("lib/") and n.endswith(".so")}}
            if "assets/S3DMain.smf" in z.namelist():
                result["stk_bytes"]=z.read("assets/S3DMain.smf")
                result["stk_sha256"]=sha(result["stk_bytes"])
            return result
    except zipfile.BadZipFile as exc: raise AuditError(f"{name}: invalid APK ZIP: {exc}") from exc

def inspect_xapk(path: pathlib.Path) -> dict[str,Any]:
    try:
        raw=path.read_bytes()
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            bad=z.testzip()
            if bad: raise AuditError(f"{path.name}: outer ZIP CRC failure at {bad}")
            if "manifest.json" not in z.namelist(): raise AuditError(f"{path.name}: manifest.json missing")
            manifest=json.loads(z.read("manifest.json"))
            rows=manifest.get("split_apks")
            if not isinstance(rows,list) or not rows: raise AuditError("XAPK split_apks list missing")
            split_files={}
            for row in rows:
                fn=row.get("file") if isinstance(row,dict) else None
                if not isinstance(fn,str) or pathlib.PurePosixPath(fn).name!=fn or not fn.endswith(".apk") or fn not in z.namelist():
                    raise AuditError(f"invalid or missing split path: {fn!r}")
                if fn in split_files: raise AuditError(f"duplicate split declaration: {fn}")
                split_files[fn]=inspect_apk_bytes(z.read(fn),fn)
            if len(split_files)!=len(rows): raise AuditError("split manifest count mismatch")
            if sum(z.getinfo(fn).file_size for fn in split_files)!=int(manifest.get("total_size",-1)):
                raise AuditError("XAPK total_size disagrees with embedded APK sizes")
            if {s["package_id"] for s in split_files.values()}!={manifest.get("package_name")}:
                raise AuditError("split package ID disagrees with XAPK manifest")
            if BASE_SPLIT not in split_files: raise AuditError("expected base APK missing")
            base=split_files[BASE_SPLIT]
            if base["version_name"]!=manifest.get("version_name"): raise AuditError("XAPK/base version mismatch")
            return {"name":path.name,"path":str(path),"bytes":len(raw),"sha256":sha(raw),
                    "outer_zip_crc":"PASS","package_name":manifest.get("package_name"),
                    "version_name":manifest.get("version_name"),"manifest_total_size":manifest.get("total_size"),
                    "split_names":sorted(split_files),"split_count":len(split_files),"splits":split_files,
                    "base":base,"manifest":manifest}
    except zipfile.BadZipFile as exc: raise AuditError(f"{path.name}: invalid XAPK ZIP: {exc}") from exc
    except json.JSONDecodeError as exc: raise AuditError(f"{path.name}: invalid manifest JSON: {exc}") from exc

def compare_stk(source_bytes: bytes, candidate_bytes: bytes, expected_path: str=EXPECTED_STK_PATH) -> dict[str,Any]:
    source=StkArchive(source_bytes,"stock STK")
    candidate=StkArchive(candidate_bytes,"candidate STK")
    if source.version!=candidate.version or source.count!=candidate.count:
        raise AuditError("STK version or entry count differs")
    se={e.name:e for e in source.entries}; ce={e.name:e for e in candidate.entries}
    if se.keys()!=ce.keys(): raise AuditError("STK entry inventory differs")
    changed=[]; decoded=0
    for name, old in se.items():
        a=source.decode(old); b=candidate.decode(ce[name]); decoded+=len(a)
        if a!=b: changed.append({"path":name,"source_bytes":len(a),"candidate_bytes":len(b),
                                 "source_sha256":sha(a),"candidate_sha256":sha(b)})
    if len(changed)!=1 or changed[0]["path"]!=expected_path:
        raise AuditError(f"expected only {expected_path}; changed paths={[x['path'] for x in changed]}")
    return {"source_sha256":sha(source_bytes),"candidate_sha256":sha(candidate_bytes),
            "version":source.version,"entry_count":source.count,"decoded_source_bytes":decoded,
            "decoded_entries_checked":len(se),"changed_entries":changed,
            "all_unchanged_entries_identical":True}

def audit(stock_path: pathlib.Path, candidate_xapk_path: pathlib.Path, candidate_apk_path: pathlib.Path,
          pin_hashes: bool=True) -> dict[str,Any]:
    stock=inspect_xapk(stock_path); candidate=inspect_xapk(candidate_xapk_path)
    standalone=inspect_apk_bytes(candidate_apk_path.read_bytes(),candidate_apk_path.name)
    if pin_hashes:
        for label,got,want in [
            ("stock XAPK",stock["sha256"],STOCK_SHA),
            ("candidate XAPK",candidate["sha256"],CAND_XAPK_SHA),
            ("standalone candidate APK",standalone["sha256"],CAND_APK_SHA)]:
            if got!=want: raise AuditError(f"{label} SHA-256 mismatch: got {got}, expected {want}")
    if stock["split_names"]!=candidate["split_names"]: raise AuditError("split-name inventory differs")
    if (stock["package_name"],stock["version_name"])!=(candidate["package_name"],candidate["version_name"]):
        raise AuditError("stock/candidate package identity differs")
    if (stock["package_name"],stock["version_name"])!=(standalone["package_id"],standalone["version_name"]):
        raise AuditError("standalone package identity differs")
    split_diffs={}
    for name in stock["split_names"]:
        left,right=stock["splits"][name],candidate["splits"][name]
        changes=changed_payload_paths(left["payload_hashes"],right["payload_hashes"])
        if changes: split_diffs[name]=changes
    if split_diffs!={BASE_SPLIT:["assets/S3DMain.smf"]}:
        raise AuditError(f"unexpected split APK payload changes: {split_diffs}")
    dexes=(stock["base"]["classes_dex_sha256"],candidate["base"]["classes_dex_sha256"],standalone["classes_dex_sha256"])
    if dexes!=(DEX_SHA,DEX_SHA,DEX_SHA): raise AuditError(f"classes.dex identity mismatch: {dexes}")
    source_stk=stock["base"].get("stk_bytes"); candidate_stk=candidate["base"].get("stk_bytes")
    standalone_stk=standalone.get("stk_bytes")
    if source_stk is None or candidate_stk is None or standalone_stk is None: raise AuditError("S3DMain.smf missing")
    if sha(candidate_stk)!=sha(standalone_stk): raise AuditError("standalone STK differs from XAPK candidate STK")
    if standalone["native_hashes"]!=candidate["splits"].get("config.arm64_v8a.apk",{}).get("native_hashes"):
        raise AuditError("standalone native libraries differ from candidate ARM64 split")
    stk=compare_stk(source_stk,candidate_stk)
    if stk["candidate_sha256"]!=candidate["base"]["stk_sha256"]: raise AuditError("STK summary hash mismatch")
    return {
        "schema":"dq-v50-actual-package-audit-v68","status":"PASS_STATIC_ONLY",
        "stock_xapk":{k:stock[k] for k in ("name","bytes","sha256","package_name","version_name","split_count","outer_zip_crc","manifest_total_size")},
        "candidate_xapk":{k:candidate[k] for k in ("name","bytes","sha256","package_name","version_name","split_count","outer_zip_crc","manifest_total_size")},
        "candidate_standalone_apk":{k:standalone.get(k) for k in ("name","bytes","sha256","package_id","version_name","entry_count","zip_crc")},
        "split_payload_changed_paths":split_diffs,"same_split_names":True,"classes_dex_sha256":DEX_SHA,
        "classes_dex_equal_across_all_three":True,"standalone_stk_equals_candidate_xapk":True,
        "stk":stk,"native_libraries_match_candidate_arm64_split":True,
        "runtime_status":"NOT_TESTED",
        "runtime_gates":{"install":False,"launch":False,"gold_button_visible":False,"touch_dispatch":False,
                         "exact_gold_delta":False,"save_reload":False,"save_recovery":False,"crash_regression":False},
        "signing_limit":"Content comparison omits JAR/v1 signature metadata; this is not apksigner v2/v3 validation or proof of PackageManager acceptance."
    }

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stock-xapk",type=pathlib.Path,required=True)
    p.add_argument("--candidate-xapk",type=pathlib.Path,required=True)
    p.add_argument("--candidate-arm64-apk",type=pathlib.Path,required=True)
    p.add_argument("--output",type=pathlib.Path,required=True)
    p.add_argument("--no-pin-hashes",action="store_true")
    a=p.parse_args()
    try:
        if a.output.exists(): raise AuditError(f"refusing to overwrite report: {a.output}")
        result=audit(a.stock_xapk,a.candidate_xapk,a.candidate_arm64_apk,not a.no_pin_hashes)
        a.output.parent.mkdir(parents=True,exist_ok=True)
        a.output.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 0
    except (OSError,ValueError,KeyError,TypeError,zipfile.BadZipFile,json.JSONDecodeError) as exc:
        print(json.dumps({"schema":"dq-v50-actual-package-audit-v68","status":"FAIL","error":str(exc)},indent=2))
        return 2
if __name__=="__main__": raise SystemExit(main())
