#!/usr/bin/env python3
"""Build a v76 startup-isolation APK using the exact stock S3DMain.smf payload.

All inputs are local. A local diagnostic signing key is used; this does not
create an update compatible with the publisher-signed application.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, tempfile, zipfile
from pathlib import Path

EXPECTED_V74_SHA = "6185a5f85eaf80ec3cc290cc10e2f0539a5e4ef9eb43ea51b1bae7b4feceda8e"
EXPECTED_STOCK_STK_SHA = "340df84310eefc21555fdd3616ad8bc4cec16aa4ed71ee9a57e7e18c3fe737e3"
EXPECTED_STOCK_DEX_SHA = "bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
OLD_ID, NEW_ID = "com.shinybox.dqv74", "com.shinybox.dqv76"
OLD_LABEL, NEW_LABEL = b"DQ v74 Tester", b"DQ v76 Tester"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def run_checked(args: list[str | Path], label: str) -> str:
    p = subprocess.run([str(x) for x in args], capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(f"{label} failed ({p.returncode}):\n{p.stdout}\n{p.stderr}")
    return p.stdout + p.stderr

def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--v74-base", required=True, type=Path)
    p.add_argument("--official-stock-apk", required=True, type=Path)
    p.add_argument("--tools-dir", required=True, type=Path, help="Android build-tools directory containing aapt, apksigner, zipalign")
    p.add_argument("--output-apk", required=True, type=Path)
    p.add_argument("--report-json", type=Path)
    p.add_argument("--keystore", required=True, type=Path)
    p.add_argument("--keystore-password-env", default="DQ_V76_KEYSTORE_PASS")
    p.add_argument("--alias", default="dqv76baseline")
    args = p.parse_args()
    base, stock_apk, tools = args.v74_base.resolve(), args.official_stock_apk.resolve(), args.tools_dir.resolve()
    output, key = args.output_apk.resolve(), args.keystore.resolve()
    report_path = args.report_json.resolve() if args.report_json else output.with_suffix(".report.json")
    password = os.environ.get(args.keystore_password_env)
    if not password:
        raise ValueError(f"set environment variable {args.keystore_password_env}; never store key passwords in source")
    for f in (base, stock_apk, tools/"aapt", tools/"apksigner", tools/"zipalign"):
        if not f.is_file():
            raise FileNotFoundError(f)
    if output.exists() or report_path.exists() or output.with_suffix(".unsigned.apk").exists():
        raise FileExistsError("refusing to overwrite output, report, or unsigned APK")
    if sha(base.read_bytes()) != EXPECTED_V74_SHA:
        raise ValueError("v74 base APK hash mismatch")
    with zipfile.ZipFile(stock_apk) as z:
        if z.testzip():
            raise ValueError("stock source APK ZIP CRC failed")
        stock_stk = z.read("assets/S3DMain.smf")
    if sha(stock_stk) != EXPECTED_STOCK_STK_SHA:
        raise ValueError("official stock STK hash mismatch")

    with zipfile.ZipFile(base) as src:
        if src.testzip():
            raise ValueError("v74 base APK ZIP CRC failed")
        manifest, resources = src.read("AndroidManifest.xml"), src.read("resources.arsc")
        old_u, new_u = OLD_ID.encode("utf-16le"), NEW_ID.encode("utf-16le")
        if len(old_u) != len(new_u) or manifest.count(old_u) != 3:
            raise ValueError("manifest package/authority layout unexpected")
        manifest = manifest.replace(old_u, new_u)
        if resources.count(old_u) != 1 or len(OLD_LABEL) != len(NEW_LABEL) or resources.count(OLD_LABEL) != 1:
            raise ValueError("resource table identity layout unexpected")
        resources = resources.replace(old_u, new_u, 1).replace(OLD_LABEL, NEW_LABEL, 1)
        unsigned = output.with_suffix(".unsigned.apk")
        seen: set[str] = set()
        with zipfile.ZipFile(unsigned, "w", allowZip64=True) as dst:
            for info in src.infolist():
                name = info.filename
                if name in seen: raise ValueError("duplicate APK path: " + name)
                seen.add(name)
                if name.upper().startswith("META-INF/"): continue
                if name == "AndroidManifest.xml": data = manifest
                elif name == "resources.arsc": data = resources
                elif name == "assets/S3DMain.smf": data = stock_stk
                else: data = src.read(name)
                ni = zipfile.ZipInfo(name, date_time=info.date_time)
                ni.compress_type, ni.comment, ni.extra = info.compress_type, info.comment, info.extra
                ni.internal_attr, ni.external_attr = info.internal_attr, info.external_attr
                dst.writestr(ni, data, compress_type=info.compress_type,
                             compresslevel=9 if info.compress_type == zipfile.ZIP_DEFLATED else None)
    try:
        with zipfile.ZipFile(unsigned) as z:
            if z.testzip(): raise ValueError("unsigned APK ZIP CRC failed")
            if sha(z.read("assets/S3DMain.smf")) != EXPECTED_STOCK_STK_SHA: raise ValueError("stock STK changed")
            if sha(z.read("classes.dex")) != EXPECTED_STOCK_DEX_SHA: raise ValueError("stock DEX mismatch")
        if not key.exists():
            run_checked(["keytool", "-genkeypair", "-keystore", key, "-storepass", password,
                         "-keypass", password, "-alias", args.alias, "-keyalg", "RSA", "-keysize", "2048",
                         "-validity", "10000", "-dname", "CN=DQ v76 Stock STK Baseline Diagnostic"], "create diagnostic key")
        with tempfile.TemporaryDirectory(prefix="dqv76-build-") as td:
            aligned = Path(td) / "aligned.apk"
            run_checked([tools/"zipalign", "-f", "-P", "16", "4", unsigned, aligned], "pre-sign zipalign")
            run_checked([tools/"zipalign", "-c", "-P", "16", "-v", "4", aligned], "verify pre-sign alignment")
            run_checked([tools/"apksigner", "sign", "--ks", key, "--ks-key-alias", args.alias,
                         "--ks-pass", f"pass:{password}", "--key-pass", f"pass:{password}",
                         "--alignment-preserved", "--lib-page-alignment", "16384", "--out", output, aligned], "sign APK")
        verify = run_checked([tools/"apksigner", "verify", "--verbose", "--print-certs", output], "verify APK signature")
        run_checked([tools/"zipalign", "-c", "-P", "16", "-v", "4", output], "verify post-sign alignment")
        badging = run_checked([tools/"aapt", "dump", "badging", output], "aapt badging")
        if f"package: name='{NEW_ID}'" not in badging or f"application-label:'{NEW_LABEL.decode()}'" not in badging:
            raise ValueError("aapt package ID or label mismatch")
        with zipfile.ZipFile(output) as z:
            if z.testzip(): raise ValueError("signed APK ZIP CRC failed")
            if sha(z.read("assets/S3DMain.smf")) != EXPECTED_STOCK_STK_SHA: raise ValueError("signed APK stock STK mismatch")
            if sha(z.read("classes.dex")) != EXPECTED_STOCK_DEX_SHA: raise ValueError("signed APK stock DEX mismatch")
            if z.read("AndroidManifest.xml").count(new_u) != 3 or z.read("resources.arsc").count(new_u) != 1:
                raise ValueError("package/provider identity mismatch")
        cert = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)", verify)
        if not cert: raise ValueError("signer certificate hash missing")
        report = {
            "schema":"dq-v76-stock-stk-startup-isolation",
            "status":"STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_TESTED",
            "artifact":{"file_name":output.name,"size_bytes":output.stat().st_size,"sha256":sha(output.read_bytes()),
                        "package_id":NEW_ID,"launcher_label":NEW_LABEL.decode(),"abi":"arm64-v8a","version_name":"3.3.2.0"},
            "inputs":{"v74_base_sha256":sha(base.read_bytes()),"stock_source_apk_sha256":sha(stock_apk.read_bytes()),
                      "stock_stk_sha256":EXPECTED_STOCK_STK_SHA,"stock_dex_sha256":EXPECTED_STOCK_DEX_SHA},
            "isolation":{"S3DMain_smf_is_exact_official_stock_copy":True,"gold_hud_patch_removed":True,
                         "package_id_updated_from_v74":True,"all_3_manifest_id_authority_strings_updated":True,
                         "resource_table_package_updated":True,"launcher_label_updated":True,"native_probe_bridge_absent":True},
            "static_validation":{"zip_crc":"PASS","zipalign_16k_pre_sign":"PASS","zipalign_16k_post_sign":"PASS",
                "apksigner_v1":"PASS" if "Verified using v1 scheme (JAR signing): true" in verify else "NOT_CONFIRMED",
                "apksigner_v2":"PASS" if "Verified using v2 scheme (APK Signature Scheme v2): true" in verify else "NOT_CONFIRMED",
                "apksigner_v3":"PASS" if "Verified using v3 scheme (APK Signature Scheme v3): true" in verify else "NOT_CONFIRMED",
                "aapt_package_label":"PASS","stock_dex_hash":"PASS","exact_stock_stk_hash":"PASS"},
            "signing":{"kind":"local diagnostic test certificate","certificate_sha256":cert.group(1).lower(),
                       "matches_official_signer":False,"private_key_in_repository":False,"private_key_shared":False},
            "runtime":{"device_install_tested":False,"device_launch_tested":False,"force_close_fixed_on_device":False,
                       "gold_runtime_checks":"not attempted","promotion_allowed":False},
            "purpose":"A/B isolate the modified v50 pause HUD payload from package/manifest/provider and stock DEX variables.",
            "promotion_allowed":False
        }
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2))
        return 0
    finally:
        unsigned.unlink(missing_ok=True)

if __name__ == "__main__":
    raise SystemExit(main())
