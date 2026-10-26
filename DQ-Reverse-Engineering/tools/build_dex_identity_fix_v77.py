#!/usr/bin/env python3
"""Build v77 by synchronizing DEX app-identity literals with a cloned APK package."""
from __future__ import annotations
import argparse, hashlib, json, os, re, struct, subprocess, tempfile, zipfile, zlib
from pathlib import Path

BASE_SHA = "c726c1d1ae6ddb834ffcae6f59b2797e05b752174865a44239c9abcd22b9bb8d"
STOCK_STK_SHA = "340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3"
STOCK_DEX_SHA = "bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
OLD_ID, NEW_ID = "com.shinybox.dqv76", "com.shinybox.dqv77"
OLD_LABEL, NEW_LABEL = b"DQ v76 Tester", b"DQ v77 Tester"
OLD_DEX_ID = b"com.shinybox.smash"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run(args: list[str | Path], label: str) -> str:
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"{label} failed ({p.returncode})\\n{p.stdout}\\n{p.stderr}")
    return p.stdout + p.stderr

def patch_dex(dex: bytes) -> tuple[bytes, dict]:
    new_id = NEW_ID.encode("ascii")
    if not dex.startswith(b"dex\\n") or len(dex) < 0x70:
        raise ValueError("invalid DEX header")
    if len(OLD_DEX_ID) != len(new_id):
        raise ValueError("the DEX literal replacement must preserve byte length")
    count = dex.count(OLD_DEX_ID)
    if count != 1:
        raise ValueError(f"expected one dotted DEX app-ID literal; found {count}")
    out = bytearray(dex.replace(OLD_DEX_ID, new_id, 1))
    out[12:32] = hashlib.sha1(out[32:]).digest()
    struct.pack_into("<I", out, 8, zlib.adler32(out[12:]) & 0xffffffff)
    final = bytes(out)
    if final[12:32] != hashlib.sha1(final[32:]).digest():
        raise ValueError("DEX SHA-1 signature mismatch")
    if struct.unpack_from("<I", final, 8)[0] != zlib.adler32(final[12:]) & 0xffffffff:
        raise ValueError("DEX Adler32 mismatch")
    if final.count(OLD_DEX_ID) or final.count(new_id) != 1:
        raise ValueError("DEX identity literal failed post-patch check")
    if b"Lcom/shinybox/smash/" not in final:
        raise ValueError("expected Java class descriptor namespace disappeared")
    return final, {"input_dex_sha256":sha(dex),"output_dex_sha256":sha(final),
                   "literal_before":count,"literal_old_after":final.count(OLD_DEX_ID),
                   "literal_new_after":final.count(new_id),"sha1_recomputed":True,
                   "adler32_recomputed":True,"class_descriptors_preserved":True}

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v76-apk",required=True,type=Path)
    p.add_argument("--tools-dir",required=True,type=Path)
    p.add_argument("--keystore",required=True,type=Path)
    p.add_argument("--output-apk",required=True,type=Path)
    p.add_argument("--report-json",type=Path)
    p.add_argument("--keystore-password-env",default="DQ_V76_KEYSTORE_PASS")
    p.add_argument("--alias",default="dqv76baseline")
    a=p.parse_args()
    base,tools,key,out=(x.resolve() for x in (a.v76_apk,a.tools_dir,a.keystore,a.output_apk))
    report_path=a.report_json.resolve() if a.report_json else out.with_suffix(".report.json")
    password=os.environ.get(a.keystore_password_env)
    if not password: raise ValueError("missing keystore password environment variable "+a.keystore_password_env)
    for f in (base,tools/"aapt",tools/"apksigner",tools/"zipalign",key):
        if not f.is_file(): raise FileNotFoundError(f)
    if out.exists() or report_path.exists() or out.with_suffix(".unsigned.apk").exists():
        raise FileExistsError("refusing to overwrite output, report, or unsigned APK")
    if sha(base.read_bytes())!=BASE_SHA: raise ValueError("v76 baseline SHA-256 mismatch")
    with zipfile.ZipFile(base) as src:
        if src.testzip(): raise ValueError("v76 APK ZIP CRC failure")
        manifest=src.read("AndroidManifest.xml")
        resources=src.read("resources.arsc")
        dex=src.read("classes.dex")
        stk=src.read("assets/S3DMain.smf")
        if sha(stk)!=STOCK_STK_SHA: raise ValueError("stock STK SHA-256 mismatch")
        if sha(dex)!=STOCK_DEX_SHA: raise ValueError("stock DEX SHA-256 mismatch")
        old_u,new_u=OLD_ID.encode("utf-16le"),NEW_ID.encode("utf-16le")
        if len(old_u)!=len(new_u) or manifest.count(old_u)!=3: raise ValueError("unexpected manifest identity layout")
        manifest=manifest.replace(old_u,new_u)
        if resources.count(old_u)!=1: raise ValueError("unexpected resource package identity layout")
        resources=resources.replace(old_u,new_u,1)
        if len(OLD_LABEL)!=len(NEW_LABEL) or resources.count(OLD_LABEL)!=1: raise ValueError("unexpected label layout")
        resources=resources.replace(OLD_LABEL,NEW_LABEL,1)
        dex_out,dex_report=patch_dex(dex)
        unsigned=out.with_suffix(".unsigned.apk")
        seen=set()
        with zipfile.ZipFile(unsigned,"w",allowZip64=True) as dst:
            for info in src.infolist():
                name=info.filename
                if name in seen: raise ValueError("duplicate APK member "+name)
                seen.add(name)
                if name.upper().startswith("META-INF/"): continue
                data={"AndroidManifest.xml":manifest,"resources.arsc":resources,"classes.dex":dex_out}.get(name)
                if data is None: data=src.read(name)
                ni=zipfile.ZipInfo(name,date_time=info.date_time)
                ni.compress_type,ni.comment,ni.extra=info.compress_type,info.comment,info.extra
                ni.internal_attr,ni.external_attr=info.internal_attr,info.external_attr
                dst.writestr(ni,data,compress_type=info.compress_type,
                             compresslevel=9 if info.compress_type==zipfile.ZIP_DEFLATED else None)
    try:
        with zipfile.ZipFile(unsigned) as z:
            if z.testzip(): raise ValueError("unsigned APK ZIP CRC failure")
            if sha(z.read("assets/S3DMain.smf"))!=STOCK_STK_SHA: raise ValueError("STK changed")
            if sha(z.read("classes.dex"))!=dex_report["output_dex_sha256"]: raise ValueError("patched DEX mismatch")
        with tempfile.TemporaryDirectory(prefix="dqv77-") as td:
            aligned=Path(td)/"aligned.apk"
            run([tools/"zipalign","-f","-P","16","4",unsigned,aligned],"pre-sign zipalign")
            run([tools/"zipalign","-c","-P","16","-v","4",aligned],"pre-sign alignment check")
            run([tools/"apksigner","sign","--ks",key,"--ks-key-alias",a.alias,
                 "--ks-pass",f"pass:{password}","--key-pass",f"pass:{password}",
                 "--alignment-preserved","--lib-page-alignment","16384","--out",out,aligned],"APK signing")
        verify=run([tools/"apksigner","verify","--verbose","--print-certs",out],"APK signature check")
        run([tools/"zipalign","-c","-P","16","-v","4",out],"post-sign alignment check")
        badging=run([tools/"aapt","dump","badging",out],"aapt badging")
        if f"package: name='{NEW_ID}'" not in badging or f"application-label:'{NEW_LABEL.decode()}'" not in badging:
            raise ValueError("aapt package/label mismatch")
        with zipfile.ZipFile(out) as z:
            if z.testzip(): raise ValueError("signed APK ZIP CRC failure")
            final_manifest,final_resources,final_dex=z.read("AndroidManifest.xml"),z.read("resources.arsc"),z.read("classes.dex")
            if final_manifest.count(new_u)!=3 or final_resources.count(new_u)!=1: raise ValueError("manifest/resource ID mismatch")
            if final_resources.count(NEW_LABEL)!=1: raise ValueError("new label not found")
            if sha(z.read("assets/S3DMain.smf"))!=STOCK_STK_SHA: raise ValueError("signed STK mismatch")
        cert=re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)",verify)
        if not cert: raise ValueError("signer certificate digest missing")
        report={"schema":"dq-v77-dex-package-identity-fix","status":"STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_TESTED",
          "artifact":{"file_name":out.name,"size_bytes":out.stat().st_size,"sha256":sha(out.read_bytes()),
            "package_id":NEW_ID,"launcher_label":NEW_LABEL.decode(),"abi":"arm64-v8a"},
          "dex_patch":dex_report,"stock_stk_sha256":STOCK_STK_SHA,
          "static_validation":{"zip_crc":"PASS","dex_header_sha1_adler32":"PASS",
            "apksigner_v1":"PASS" if "Verified using v1 scheme (JAR signing): true" in verify else "NOT_CONFIRMED",
            "apksigner_v2":"PASS" if "Verified using v2 scheme (APK Signature Scheme v2): true" in verify else "NOT_CONFIRMED",
            "apksigner_v3":"PASS" if "Verified using v3 scheme (APK Signature Scheme v3): true" in verify else "NOT_CONFIRMED",
            "zipalign_16k_pre_sign":"PASS","zipalign_16k_post_sign":"PASS","aapt_package_label":"PASS",
            "stock_stk_hash":"PASS","manifest_resource_identity":"PASS"},
          "signing":{"kind":"local diagnostic test certificate","certificate_sha256":cert.group(1).lower(),
            "matches_official_signer":False},
          "runtime":{"device_install_tested":False,"device_launch_tested":False,
            "force_close_fixed_on_device":False,"promotion_allowed":False},"promotion_allowed":False}
        report_path.parent.mkdir(parents=True,exist_ok=True)
        report_path.write_text(json.dumps(report,indent=2)+"\\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 0
    finally:
        unsigned.unlink(missing_ok=True)

if __name__=="__main__": raise SystemExit(main())
