#!/usr/bin/env python3
"""Build a side-by-side v73 comparator with stock DEX and no native probe bridge.

Inputs must be kept locally. The tool intentionally has no hard-coded signing password.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, zipfile
from pathlib import Path
import tempfile

BASE_SHA = "6261d077092098986094ebcf79522b767143467b7b3bc074341b2da6700098b6"
CANDIDATE_SHA = "f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa"
STOCK_DEX_SHA = "bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
STK_SHA = "e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e"
BRIDGE_SHA = "82f19bbe8aec8ac95030a5e0f773168f0b3a5bfde76e1fe334f103415f8e0fd5"
OLD_ID, NEW_ID = "com.shinybox.dqv72", "com.shinybox.dqv73"
OLD_LABEL, NEW_LABEL = b"DQ v72 Tester", b"DQ v73 Tester"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run_checked(args: list[str | Path], label: str) -> str:
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"{label} failed ({p.returncode}):\n{p.stdout}\n{p.stderr}")
    return p.stdout + p.stderr

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v72-base", type=Path, required=True)
    p.add_argument("--v50-candidate-apk", type=Path, required=True)
    p.add_argument("--tools-dir", type=Path, required=True)
    p.add_argument("--output-apk", type=Path, required=True)
    p.add_argument("--keystore", type=Path, required=True)
    p.add_argument("--keystore-password-env", default="DQ_V73_KEYSTORE_PASS")
    p.add_argument("--alias", default="dqv73diag")
    p.add_argument("--report-json", type=Path)
    args = p.parse_args()
    base, candidate, tools = args.v72_base.resolve(), args.v50_candidate_apk.resolve(), args.tools_dir.resolve()
    output, key = args.output_apk.resolve(), args.keystore.resolve()
    report_path = args.report_json.resolve() if args.report_json else output.with_suffix(".report.json")
    password = os.environ.get(args.keystore_password_env)
    if not password:
        raise ValueError(f"set environment variable {args.keystore_password_env}; do not store key passwords in source")
    for f in (base,candidate,tools/"aapt",tools/"apksigner",tools/"zipalign"):
        if not f.is_file():
            raise FileNotFoundError(f)
    if output.exists() or report_path.exists() or output.with_suffix(".unsigned.apk").exists():
        raise FileExistsError("refusing to overwrite output or report")
    if sha(base.read_bytes()) != BASE_SHA:
        raise ValueError("v72 base APK hash mismatch")
    if sha(candidate.read_bytes()) != CANDIDATE_SHA:
        raise ValueError("v50 candidate APK hash mismatch")
    with zipfile.ZipFile(candidate) as stock:
        if stock.testzip():
            raise ValueError("candidate APK CRC failed")
        dex, stk = stock.read("classes.dex"), stock.read("assets/S3DMain.smf")
    if sha(dex) != STOCK_DEX_SHA or sha(stk) != STK_SHA:
        raise ValueError("candidate stock DEX or STK hash mismatch")
    with zipfile.ZipFile(base) as src:
        if src.testzip():
            raise ValueError("v72 base ZIP CRC failed")
        manifest = src.read("AndroidManifest.xml")
        old_utf16, new_utf16 = OLD_ID.encode("utf-16le"), NEW_ID.encode("utf-16le")
        if len(old_utf16) != len(new_utf16) or manifest.count(old_utf16) != 1:
            raise ValueError("manifest package string layout changed; refusing patch")
        manifest = manifest.replace(old_utf16, new_utf16, 1)
        resources = src.read("resources.arsc")
        if resources.count(old_utf16) != 1:
            raise ValueError("resources package string layout changed; refusing patch")
        resources = resources.replace(old_utf16, new_utf16, 1)
        if len(OLD_LABEL) != len(NEW_LABEL) or resources.count(OLD_LABEL) != 1:
            raise ValueError("launcher label layout changed; refusing patch")
        resources = resources.replace(OLD_LABEL, NEW_LABEL, 1)
        unsigned = output.with_suffix(".unsigned.apk")
        with zipfile.ZipFile(unsigned,"w",allowZip64=True) as dst:
            seen: set[str] = set()
            for info in src.infolist():
                name = info.filename
                if name in seen:
                    raise ValueError("duplicate APK path: " + name)
                seen.add(name)
                if name.upper().startswith("META-INF/") or name == "lib/arm64-v8a/libdqbridge.so":
                    continue
                if name == "classes.dex":
                    data = dex
                elif name == "AndroidManifest.xml":
                    data = manifest
                elif name == "resources.arsc":
                    data = resources
                else:
                    data = src.read(name)
                ni = zipfile.ZipInfo(name, date_time=info.date_time)
                ni.compress_type, ni.comment, ni.extra = info.compress_type, info.comment, info.extra
                ni.internal_attr, ni.external_attr = info.internal_attr, info.external_attr
                dst.writestr(ni,data,compress_type=info.compress_type,
                             compresslevel=9 if info.compress_type == zipfile.ZIP_DEFLATED else None)
    try:
        with zipfile.ZipFile(unsigned) as check:
            if check.testzip():
                raise ValueError("unsigned APK CRC failed")
            if sha(check.read("classes.dex")) != STOCK_DEX_SHA:
                raise ValueError("stock DEX payload mismatch")
            if sha(check.read("assets/S3DMain.smf")) != STK_SHA:
                raise ValueError("STK payload changed")
            if "lib/arm64-v8a/libdqbridge.so" in check.namelist():
                raise ValueError("native probe bridge unexpectedly remains")
            if b"DqNativeProbe" in check.read("classes.dex"):
                raise ValueError("native probe class unexpectedly remains")
        if not key.exists():
            run_checked(["keytool","-genkeypair","-keystore",key,"-storepass",password,
                         "-keypass",password,"-alias",args.alias,"-keyalg","RSA","-keysize","2048",
                         "-validity","10000","-dname","CN=DQ v73 No Native Probe Diagnostic"],
                        "create local test keystore")
        with tempfile.TemporaryDirectory(prefix="dqv73-build-") as td:
            aligned = Path(td) / "aligned.apk"
            run_checked([tools/"zipalign","-f","-P","16","4",unsigned,aligned],"pre-sign zipalign")
            run_checked([tools/"zipalign","-c","-P","16","-v","4",aligned],"pre-sign alignment verification")
            run_checked([tools/"apksigner","sign","--ks",key,"--ks-key-alias",args.alias,
                         "--ks-pass",f"pass:{password}","--key-pass",f"pass:{password}",
                         "--alignment-preserved","--lib-page-alignment","16384","--out",output,aligned],
                        "apksigner sign")
        verify = run_checked([tools/"apksigner","verify","--verbose","--print-certs",output],"apksigner verify")
        run_checked([tools/"zipalign","-c","-P","16","-v","4",output],"post-sign alignment verification")
        badging = run_checked([tools/"aapt","dump","badging",output],"aapt dump badging")
        if f"package: name='{NEW_ID}'" not in badging or f"application-label:'{NEW_LABEL.decode()}'" not in badging:
            raise ValueError("aapt package ID or label mismatch")
        with zipfile.ZipFile(output) as check:
            if check.testzip():
                raise ValueError("signed APK CRC failed")
            if "lib/arm64-v8a/libdqbridge.so" in check.namelist():
                raise ValueError("probe bridge still present after signing")
        cert = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)", verify)
        if not cert:
            raise ValueError("apksigner did not return the signer digest")
        report = {
            "schema":"dq-no-native-probe-comparator-v73",
            "status":"STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_TESTED",
            "artifact":{"file_name":output.name,"size_bytes":output.stat().st_size,"sha256":sha(output.read_bytes()),
                        "package_id":NEW_ID,"launcher_label":NEW_LABEL.decode(),"abi":"arm64-v8a",
                        "version_name":"3.3.2.0","split_count":1},
            "inputs":{"v72_base_sha256":sha(base.read_bytes()),"stock_dex_sha256":sha(dex),
                      "stk_sha256":sha(stk),"v72_bridge_sha256_removed":BRIDGE_SHA},
            "isolation_changes":{"stock_classes_dex_restored":True,"libdqbridge_removed":True,
                                 "native_probe_jni_invocations_present":False,"gold_hud_stk_preserved":True,
                                 "application_id_is_separate":True,"package_id_changed_from_v72":OLD_ID},
            "static_validation":{"zip_crc":"PASS","zipalign_16k_pre_sign":"PASS","zipalign_16k_post_sign":"PASS",
                                 "apksigner_v1":"PASS" if "Verified using v1 scheme (JAR signing): true" in verify else "NOT_CONFIRMED",
                                 "apksigner_v2":"PASS" if "Verified using v2 scheme (APK Signature Scheme v2): true" in verify else "NOT_CONFIRMED",
                                 "apksigner_v3":"PASS" if "Verified using v3 scheme (APK Signature Scheme v3): true" in verify else "NOT_CONFIRMED",
                                 "aapt_badging":"PASS","package_id":"PASS","launcher_label":"PASS",
                                 "stock_dex_sha256":"PASS","bridge_absent":"PASS","stk_hash_preserved":"PASS"},
            "signing":{"kind":"local diagnostic test certificate","certificate_sha256":cert.group(1).lower(),
                       "matches_official_signer":False,"private_key_in_repository":False,"private_key_shared":False},
            "runtime":{"device_install_tested":False,"device_start_tested":False,
                       "force_close_reproduced_or_cleared":False,"native_callback_invoked":False,
                       "gold_plus_100k_runtime_checks":"0/9","catalog_runtime_verified":"0/222",
                       "promotion_allowed":False},
            "limitations":["No physical-device install or launch was performed by this build environment.",
                           "Static validation does not prove installability or runtime stability.",
                           "The package uses a local test key and does not update the publisher-signed app.",
                           "The Gold HUD remains unverified and catalogue integration remains 0/222.",
                           "The force-close cause is not confirmed until an A/B device result or crash log is available."],
            "promotion_allowed":False
        }
        report_path.parent.mkdir(parents=True,exist_ok=True)
        report_path.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 0
    finally:
        unsigned.unlink(missing_ok=True)

if __name__ == "__main__":
    raise SystemExit(main())