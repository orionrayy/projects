#!/usr/bin/env python3
"""Build a separate-package v72 ARM64 diagnostic APK from pinned local inputs.

Requires official Android SDK Build Tools (apksigner, zipalign, aapt) and a
keystore password supplied through an environment variable. The source APK,
patched DEX, and native library are never overwritten. This builds a diagnostic
package only; it does not attest to device/runtime behavior.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
import struct
import subprocess
import zipfile
from pathlib import Path
from typing import Any

OLD_PACKAGE = "com.shinybox.smash"
NEW_PACKAGE = "com.shinybox.dqv72"
OLD_LABEL = b"Dungeon Quest"
NEW_LABEL = b"DQ v72 Tester"
ANDROID_NS = "http://schemas.android.com/apk/res/android"
PINNED_CANDIDATE_SHA = "f6cd9ed0011b2c7f72dff506397d24194e3ed7d3fb7aa58adea9f8e939ab6dfa"
PINNED_PATCHED_DEX_SHA = "1533a5858e8624f2dc615e5335d14afd6de983c0478271963acb985423eb4d48"
PINNED_BRIDGE_SHA = "82f19bbe8aec8ac95030a5e0f773168f0b3a5bfde76e1fe334f103415f8e0fd5"
PINNED_STK_SHA = "e17884a13c775c9aac3afce3c0003eb9ed54a3b9a32ef4a6b89bf72e6ef9f52e"
OFFICIAL_SIGNER_SHA256 = "9A28A99171C8F63F3411E291F6D96F13D5D9C1736206A0CF95EBEE99BC31421D"

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def u16(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<H", data, offset)[0]

def u32(data: bytes | bytearray, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]

def p16(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<H", data, offset, value)

def p32(data: bytearray, offset: int, value: int) -> None:
    struct.pack_into("<I", data, offset, value)

def decode_pool(data: bytes | bytearray, offset: int):
    header = u16(data, offset + 2)
    count = u32(data, offset + 8)
    flags = u32(data, offset + 16)
    strings_start = u32(data, offset + 20)
    if count > 100_000 or header < 28:
        raise ValueError("invalid Android string pool")
    offsets = [u32(data, offset + header + 4 * i) for i in range(count)]
    strings, locations = [], []

    def len8(pos: int):
        first = data[pos]
        pos += 1
        if first & 0x80:
            return ((first & 0x7f) << 8) | data[pos], pos + 1
        return first, pos

    for relative in offsets:
        pos = offset + strings_start + relative
        if flags & 0x100:
            _, pos = len8(pos)
            byte_len, pos = len8(pos)
            strings.append(data[pos:pos + byte_len].decode("utf-8", "replace"))
            locations.append((pos, byte_len, "utf8"))
        else:
            units = u16(data, pos)
            pos += 2
            if units & 0x8000:
                units = ((units & 0x7fff) << 16) | u16(data, pos)
                pos += 2
            byte_len = units * 2
            strings.append(data[pos:pos + byte_len].decode("utf-16le", "replace"))
            locations.append((pos, byte_len, "utf16"))
    return strings, locations

def manifest_package_id(data: bytes) -> str:
    if len(data) < 8 or u16(data, 0) != 3:
        raise ValueError("AndroidManifest.xml is not binary XML")
    strings, chunks = [], []
    pos = 8
    while pos + 8 <= len(data):
        kind, size, header_size = u16(data, pos), u32(data, pos + 4), u16(data, pos + 2)
        if size < 8 or pos + size > len(data):
            raise ValueError("invalid binary XML chunk")
        chunks.append((pos, kind, size, header_size))
        if kind == 1:
            strings, _ = decode_pool(data, pos)
        pos += size
    for pos, kind, _size, header_size in chunks:
        if kind != 0x0102 or header_size < 16:
            continue
        tag_index = u32(data, pos + 20)
        if tag_index >= len(strings) or strings[tag_index] != "manifest":
            continue
        attr_start, attr_size, count = u16(data, pos + 24), u16(data, pos + 26), u16(data, pos + 28)
        if attr_size < 20 or count > 4096:
            raise ValueError("invalid binary manifest attributes")
        base = pos + 16 + attr_start
        for index in range(count):
            ap = base + index * attr_size
            ns_i, name_i, raw_i = u32(data, ap), u32(data, ap + 4), u32(data, ap + 8)
            name = strings[name_i] if name_i < len(strings) else ""
            namespace = strings[ns_i] if ns_i != 0xffffffff and ns_i < len(strings) else ""
            raw = strings[raw_i] if raw_i != 0xffffffff and raw_i < len(strings) else None
            value_type, value_data = data[ap + 15], u32(data, ap + 16)
            value: Any = raw if raw is not None else (
                strings[value_data] if value_type == 3 and value_data < len(strings)
                else value_data if value_type in (16, 17) else None
            )
            if name == "package" and not namespace and isinstance(value, str):
                return value
    raise ValueError("manifest package attribute not found")

def patch_manifest(data: bytes):
    if len(OLD_PACKAGE) != len(NEW_PACKAGE) or len(OLD_PACKAGE.encode("utf-16le")) != len(NEW_PACKAGE.encode("utf-16le")):
        raise ValueError("application ID rename must preserve string-pool length")
    if len(data) < 8 or u16(data, 0) != 3:
        raise ValueError("input manifest is not binary XML")
    buffer = bytearray(data)
    strings, locations, chunks = [], [], []
    pos = 8
    while pos + 8 <= len(buffer):
        kind, size, header_size = u16(buffer, pos), u32(buffer, pos + 4), u16(buffer, pos + 2)
        if size < 8 or pos + size > len(buffer):
            raise ValueError("invalid binary XML chunk")
        chunks.append((pos, kind, size, header_size))
        if kind == 1:
            strings, locations = decode_pool(buffer, pos)
        pos += size
    exact = [i for i, value in enumerate(strings) if value == OLD_PACKAGE]
    if len(exact) != 1:
        raise ValueError(f"expected one exact package string, found {len(exact)}")
    start, byte_len, encoding = locations[exact[0]]
    replacement = NEW_PACKAGE.encode("utf-8" if encoding == "utf8" else "utf-16le")
    if len(replacement) != byte_len:
        raise ValueError("replacement package string has a different encoded length")
    buffer[start:start + byte_len] = replacement

    strings, _ = decode_pool(buffer, next(pos for pos, kind, _size, _hs in chunks if kind == 1))
    output = bytearray(buffer[:8])
    total_delta = 0
    icon_attributes_removed = 0
    for pos, kind, size, header_size in chunks:
        chunk = bytearray(buffer[pos:pos + size])
        if kind == 0x0102 and header_size >= 16:
            tag_i = u32(chunk, 20)
            tag = strings[tag_i] if tag_i < len(strings) else ""
            attr_start, attr_size, count = u16(chunk, 24), u16(chunk, 26), u16(chunk, 28)
            base = 16 + attr_start
            records = []
            for index in range(count):
                ap = base + index * attr_size
                ns_i, name_i = u32(chunk, ap), u32(chunk, ap + 4)
                name = strings[name_i] if name_i < len(strings) else ""
                namespace = strings[ns_i] if ns_i != 0xffffffff and ns_i < len(strings) else ""
                if namespace == ANDROID_NS and name == "icon":
                    icon_attributes_removed += 1
                    continue
                records.append(bytes(chunk[ap:ap + attr_size]))
            if len(records) != count:
                prefix = bytes(chunk[:base])
                suffix = bytes(chunk[base + count * attr_size:])
                delta = (count - len(records)) * attr_size
                chunk = bytearray(prefix + b"".join(records) + suffix)
                p16(chunk, 28, len(records))
                p32(chunk, 4, len(chunk))
                total_delta -= delta
        output.extend(chunk)
    if total_delta:
        p32(output, 4, len(output))
    result = bytes(output)
    if manifest_package_id(result) != NEW_PACKAGE:
        raise ValueError("binary manifest application ID rewrite failed")
    if icon_attributes_removed < 1:
        raise ValueError("expected at least one unresolved icon attribute to remove")
    return result, {
        "package_id_before": OLD_PACKAGE,
        "package_id_after": NEW_PACKAGE,
        "icon_attributes_removed": icon_attributes_removed,
        "manifest_size_delta_bytes": total_delta
    }

def run_checked(args, label: str):
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode:
        raise RuntimeError(f"{label} failed ({result.returncode}):\n{result.stdout}\n{result.stderr}")
    return result.stdout + result.stderr

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate-apk", type=Path, required=True)
    parser.add_argument("--patched-dex", type=Path, required=True)
    parser.add_argument("--bridge-so", type=Path, required=True)
    parser.add_argument("--tools-dir", type=Path, required=True,
                        help="Android Build Tools directory containing apksigner, zipalign and aapt")
    parser.add_argument("--output-apk", type=Path, required=True)
    parser.add_argument("--keystore", type=Path, required=True,
                        help="local test keystore; never commit or upload its private key")
    parser.add_argument("--keystore-password-env", default="DQ_V72_KEYSTORE_PASS")
    parser.add_argument("--alias", default="dqv72diag")
    parser.add_argument("--report-json", type=Path,
                        help="optional report output; default is OUTPUT_APK with .report.json suffix")
    args = parser.parse_args()

    apk_in, dex_path, bridge_path = args.candidate_apk.resolve(), args.patched_dex.resolve(), args.bridge_so.resolve()
    tools_dir, apk_out, keystore = args.tools_dir.resolve(), args.output_apk.resolve(), args.keystore.resolve()
    report_path = args.report_json.resolve() if args.report_json else apk_out.with_suffix(".report.json")
    password = os.environ.get(args.keystore_password_env)
    if not password:
        raise ValueError(f"set environment variable {args.keystore_password_env} to a local test-key password")
    keypass = password
    apksigner, zipalign, aapt = tools_dir / "apksigner", tools_dir / "zipalign", tools_dir / "aapt"
    for item in (apk_in, dex_path, bridge_path, apksigner, zipalign, aapt):
        if not item.is_file():
            raise FileNotFoundError(item)
    if apk_out.exists() or report_path.exists():
        raise FileExistsError("refusing to overwrite output APK or report")
    if apk_in == apk_out or dex_path == apk_out or bridge_path == apk_out:
        raise ValueError("output APK path must differ from every input")
    candidate_hash, dex_hash, bridge_hash = sha(apk_in.read_bytes()), sha(dex_path.read_bytes()), sha(bridge_path.read_bytes())
    if candidate_hash != PINNED_CANDIDATE_SHA:
        raise ValueError(f"candidate APK SHA-256 mismatch: {candidate_hash}")
    if dex_hash != PINNED_PATCHED_DEX_SHA:
        raise ValueError(f"patched DEX SHA-256 mismatch: {dex_hash}")
    if bridge_hash != PINNED_BRIDGE_SHA:
        raise ValueError(f"native bridge SHA-256 mismatch: {bridge_hash}")
    if not 0 < len(OLD_LABEL) == len(NEW_LABEL):
        raise ValueError("launcher label replacement must preserve byte length")
    apk_out.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(apk_in) as source:
        bad = source.testzip()
        if bad:
            raise ValueError(f"input APK ZIP CRC failed at {bad}")
        required = {"classes.dex", "AndroidManifest.xml", "resources.arsc", "assets/S3DMain.smf"}
        missing = required - set(source.namelist())
        if missing:
            raise ValueError(f"required source members absent: {sorted(missing)}")
        manifest, manifest_report = patch_manifest(source.read("AndroidManifest.xml"))
        resources = source.read("resources.arsc")
        old_id_utf16, new_id_utf16 = OLD_PACKAGE.encode("utf-16le"), NEW_PACKAGE.encode("utf-16le")
        if resources.count(old_id_utf16) != 1:
            raise ValueError(f"expected one exact resources.arsc package string, got {resources.count(old_id_utf16)}")
        resources = resources.replace(old_id_utf16, new_id_utf16, 1)
        if resources.count(OLD_LABEL) != 1:
            raise ValueError(f"expected one launcher label string in resources.arsc, got {resources.count(OLD_LABEL)}")
        resources = resources.replace(OLD_LABEL, NEW_LABEL, 1)

        temp_unsigned = apk_out.with_suffix(".unsigned.apk")
        if temp_unsigned.exists():
            raise FileExistsError(f"refusing to overwrite {temp_unsigned}")
        seen: set[str] = set()
        with zipfile.ZipFile(temp_unsigned, "w", allowZip64=True) as dest:
            for info in source.infolist():
                name = info.filename
                if name in seen:
                    raise ValueError(f"duplicate ZIP path: {name}")
                seen.add(name)
                if name.upper().startswith("META-INF/"):
                    continue
                if name == "classes.dex":
                    data = dex_path.read_bytes()
                elif name == "AndroidManifest.xml":
                    data = manifest
                elif name == "resources.arsc":
                    data = resources
                else:
                    data = source.read(name)
                new_info = zipfile.ZipInfo(name, date_time=info.date_time)
                new_info.compress_type = info.compress_type
                new_info.comment = info.comment
                new_info.extra = info.extra
                new_info.internal_attr = info.internal_attr
                new_info.external_attr = info.external_attr
                dest.writestr(new_info, data, compress_type=info.compress_type,
                              compresslevel=9 if info.compress_type == zipfile.ZIP_DEFLATED else None)
            if "lib/arm64-v8a/libdqbridge.so" in seen:
                raise ValueError("source candidate already contains libdqbridge.so")
            bridge_info = zipfile.ZipInfo("lib/arm64-v8a/libdqbridge.so", date_time=(2026, 10, 25, 0, 0, 0))
            bridge_info.compress_type = zipfile.ZIP_STORED
            bridge_info.external_attr = 0o100755 << 16
            dest.writestr(bridge_info, bridge_path.read_bytes(), compress_type=zipfile.ZIP_STORED)

    with zipfile.ZipFile(temp_unsigned) as check:
        if check.testzip():
            raise ValueError("unsigned APK ZIP CRC verification failed")
        if sha(check.read("classes.dex")) != PINNED_PATCHED_DEX_SHA:
            raise ValueError("patched DEX payload does not match expected digest")
        if sha(check.read("lib/arm64-v8a/libdqbridge.so")) != PINNED_BRIDGE_SHA:
            raise ValueError("native probe payload does not match expected digest")
        if manifest_package_id(check.read("AndroidManifest.xml")) != NEW_PACKAGE:
            raise ValueError("application ID mismatch after build")
        if NEW_LABEL.decode() not in check.read("resources.arsc").decode("utf-8", "ignore"):
            raise ValueError("launcher label string missing after build")

    if not keystore.exists():
        run_checked([
            "keytool", "-genkeypair", "-keystore", str(keystore), "-storepass", password,
            "-keypass", keypass, "-alias", args.alias, "-keyalg", "RSA", "-keysize", "2048",
            "-validity", "10000", "-dname", "CN=DQ v72 Diagnostic Test"
        ], "create local diagnostic keystore")

    import tempfile
    with tempfile.TemporaryDirectory(prefix="dqv72-apk-build-") as temp_dir:
        aligned = Path(temp_dir) / "aligned.apk"
        run_checked([str(zipalign), "-f", "-P", "16", "4", str(temp_unsigned), str(aligned)],
                    "pre-sign zipalign")
        run_checked([str(zipalign), "-c", "-P", "16", "-v", "4", str(aligned)],
                    "pre-sign zipalign verification")
        run_checked([
            str(apksigner), "sign", "--ks", str(keystore), "--ks-key-alias", args.alias,
            "--ks-pass", f"pass:{password}", "--key-pass", f"pass:{keypass}",
            "--alignment-preserved", "--lib-page-alignment", "16384",
            "--out", str(apk_out), str(aligned)
        ], "apksigner sign")
    signed_verify = run_checked([str(apksigner), "verify", "--verbose", "--print-certs", str(apk_out)],
                                "apksigner verify")
    run_checked([str(zipalign), "-c", "-P", "16", "-v", "4", str(apk_out)],
                "post-sign zipalign verification")
    badging = run_checked([str(aapt), "dump", "badging", str(apk_out)], "aapt dump badging")
    if f"package: name='{NEW_PACKAGE}'" not in badging or f"application-label:'{NEW_LABEL.decode()}'" not in badging:
        raise RuntimeError("aapt did not report the expected package ID and diagnostic label")
    with zipfile.ZipFile(apk_out) as final:
        if final.testzip():
            raise ValueError("final APK ZIP CRC verification failed")
    cert_match = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-fA-F]+)", signed_verify)
    if not cert_match:
        raise RuntimeError("apksigner did not report a signer certificate SHA-256")
    signer_sha256 = cert_match.group(1).upper()
    if signer_sha256 == OFFICIAL_SIGNER_SHA256:
        raise RuntimeError("diagnostic build unexpectedly uses the official signer identity")

    report = {
        "schema": "dq-diagnostic-arm64-apk-build-v72",
        "status": "BUILT_STATIC_VALIDATION_PASS_DEVICE_RUNTIME_NOT_VERIFIED",
        "artifact": {
            "file_name": apk_out.name, "size_bytes": apk_out.stat().st_size, "sha256": sha(apk_out.read_bytes()),
            "package_id": NEW_PACKAGE, "version_name": "3.3.2.0", "launcher_label": NEW_LABEL.decode(),
            "abi": "arm64-v8a", "split_count": 1
        },
        "inputs": {
            "source_candidate_apk_sha256": candidate_hash,
            "source_stk_sha256": PINNED_STK_SHA,
            "patched_dex_sha256": dex_hash,
            "bridge_sha256": bridge_hash,
            "source_candidate_package_id": OLD_PACKAGE,
            "source_stk_changed_entries": ["Resources/HUD/pause.hud"]
        },
        "package_transform": {
            "target_package_id": NEW_PACKAGE, "application_id_length_preserved": True,
            "resources_package_name_updated": True, "launcher_label_before": OLD_LABEL.decode(),
            "launcher_label_after": NEW_LABEL.decode(),
            "unresolved_icon_attributes_removed": manifest_report["icon_attributes_removed"] > 0,
            "source_app_id_preserved": OLD_PACKAGE, "original_apk_modified_in_place": False,
            "original_xapk_modified_in_place": False
        },
        "validation": {
            "outer_zip_crc": "PASS", "all_apk_zip_entries_crc": "PASS",
            "zipalign_pre_sign_16k_native": "PASS", "zipalign_post_sign_16k_native": "PASS",
            "apksigner_verify_v1": "PASS" if "Verified using v1 scheme (JAR signing): true" in signed_verify else "NOT_CONFIRMED",
            "apksigner_verify_v2": "PASS" if "Verified using v2 scheme (APK Signature Scheme v2): true" in signed_verify else "NOT_CONFIRMED",
            "apksigner_verify_v3": "PASS" if "Verified using v3 scheme (APK Signature Scheme v3): true" in signed_verify else "NOT_CONFIRMED",
            "aapt_dump_badging": "PASS", "package_id_verified_by_aapt": True,
            "launchable_activity_found": "com.shinybox.smash.Smash",
            "signer": {
                "kind": "local diagnostic test certificate",
                "certificate_sha256": signer_sha256.lower(),
                "matches_official_signer": False, "private_key_in_repository": False, "private_key_shared": False
            }
        },
        "probe_observability": {
            "log_tag": "DQv72Probe",
            "expected_markers": [
                "library_load=PASS",
                "library_load=FAIL",
                "callback_register=PASS",
                "callback_register=FAIL",
                "callback_roundtrip=PASS",
                "callback_roundtrip=FAIL",
                "callback_unregister=PASS",
                "callback_unregister=FAIL",
                "callback_probe=EXCEPTION",
                "callback_unregister=EXCEPTION"
            ],
            "runtime_logcat_captured": false,
            "runtime_markers_verified": false
        },
        "runtime_gate": {
            "installed_on_device": False, "launched_on_device": False, "offline_tested": False,
            "native_probe_roundtrip_21_to_42_verified": False, "shutdown_unregister_verified": False,
            "gold_runtime_checks_passed": 0, "gold_runtime_checks_total": 9, "catalog_items": 222,
            "catalog_routes_assigned": 0, "catalog_runtime_verified_effects": 0, "promotion_allowed": False
        },
        "limitations": [
            "This script statically packages a diagnostic build only; no Package Manager install or game launch is performed.",
            "The local test certificate is not the official publisher certificate and the new package ID creates a separate app.",
            "The native bridge callback ABI/lifetime and engine thread behavior remain unverified in the running game.",
            "All 222 catalogue effects remain disconnected and the Gold +100K candidate remains 0/9 runtime-verified."
        ],
        "promotion_allowed": False
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    temp_unsigned.unlink(missing_ok=True)
    print(json.dumps(report, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
