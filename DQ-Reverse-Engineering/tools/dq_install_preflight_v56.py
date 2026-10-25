#!/usr/bin/env python3
"""Read-only Android APK/XAPK identity and update-compatibility preflight.

Uses only Python stdlib plus JDK keytool/jarsigner. It does not install apps,
modify packages, bypass signature checks, or assert runtime compatibility.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import tempfile
import zipfile
from typing import Any

ANDROID_NS = "http://schemas.android.com/apk/res/android"


def _u16(data: bytes, offset: int) -> int:
    import struct
    return struct.unpack_from("<H", data, offset)[0]


def _u32(data: bytes, offset: int) -> int:
    import struct
    return struct.unpack_from("<I", data, offset)[0]


def _string_pool(data: bytes, offset: int) -> list[str]:
    header_size = _u16(data, offset + 2)
    count = _u32(data, offset + 8)
    flags = _u32(data, offset + 16)
    strings_start = _u32(data, offset + 20)
    if count > 100_000 or header_size < 28:
        raise ValueError("invalid Android string pool header")
    offsets = [_u32(data, offset + header_size + 4 * i) for i in range(count)]

    def len8(pos: int) -> tuple[int, int]:
        first = data[pos]
        pos += 1
        if first & 0x80:
            if pos >= len(data):
                raise ValueError("truncated UTF-8 string length")
            return ((first & 0x7f) << 8) | data[pos], pos + 1
        return first, pos

    strings: list[str] = []
    for rel in offsets:
        pos = offset + strings_start + rel
        if flags & 0x100:
            _, pos = len8(pos)
            byte_len, pos = len8(pos)
            if pos + byte_len > len(data):
                raise ValueError("truncated UTF-8 string-pool item")
            strings.append(data[pos:pos + byte_len].decode("utf-8", "replace"))
        else:
            units = _u16(data, pos)
            pos += 2
            if units & 0x8000:
                units = ((units & 0x7fff) << 16) | _u16(data, pos)
                pos += 2
            byte_len = units * 2
            if pos + byte_len > len(data):
                raise ValueError("truncated UTF-16 string-pool item")
            strings.append(data[pos:pos + byte_len].decode("utf-16le", "replace"))
    return strings


def decode_manifest_identity(data: bytes) -> dict[str, Any]:
    """Read package/version attributes from Android binary XML without rewriting it."""
    if len(data) < 8 or _u16(data, 0) != 3:
        raise ValueError("AndroidManifest.xml is not Android binary XML")
    strings: list[str] = []
    pos = 8
    while pos + 8 <= len(data):
        typ, size = _u16(data, pos), _u32(data, pos + 4)
        if size < 8 or pos + size > len(data):
            raise ValueError("invalid binary XML chunk size")
        if typ == 1:
            strings = _string_pool(data, pos)
        pos += size

    result: dict[str, Any] = {"package_id": None, "version_name": None, "version_code": None}
    pos = 8
    while pos + 8 <= len(data):
        typ, header_size, size = _u16(data, pos), _u16(data, pos + 2), _u32(data, pos + 4)
        if size < 8 or pos + size > len(data):
            raise ValueError("invalid binary XML chunk while reading manifest identity")
        if typ == 0x0102 and header_size >= 16:
            name_index = _u32(data, pos + 20)
            tag = strings[name_index] if name_index < len(strings) else ""
            if tag == "manifest":
                attr_start = _u16(data, pos + 24)
                attr_size = _u16(data, pos + 26)
                attr_count = _u16(data, pos + 28)
                if attr_size < 20 or attr_count > 4096:
                    raise ValueError("invalid manifest attribute table")
                base = pos + 16 + attr_start
                for i in range(attr_count):
                    ap = base + i * attr_size
                    ns_index, name_index, raw_index = _u32(data, ap), _u32(data, ap + 4), _u32(data, ap + 8)
                    value_type, value_data = data[ap + 15], _u32(data, ap + 16)
                    name = strings[name_index] if name_index < len(strings) else ""
                    namespace = strings[ns_index] if ns_index != 0xffffffff and ns_index < len(strings) else ""
                    raw_value = strings[raw_index] if raw_index != 0xffffffff and raw_index < len(strings) else None
                    if raw_value is not None:
                        value: Any = raw_value
                    elif value_type == 3 and value_data < len(strings):
                        value = strings[value_data]
                    elif value_type in (16, 17):
                        value = value_data
                    else:
                        value = None
                    if name == "package" and not namespace:
                        result["package_id"] = value
                    elif namespace == ANDROID_NS and name == "versionName":
                        result["version_name"] = value
                    elif namespace == ANDROID_NS and name == "versionCode":
                        result["version_code"] = value
                break
        pos += size
    if not result["package_id"]:
        raise ValueError("package attribute not found in manifest")
    return result


def _run_signing_tools(apk_path: pathlib.Path) -> dict[str, Any]:
    if not shutil.which("keytool") or not shutil.which("jarsigner"):
        return {"signer_fingerprint": None, "jarsigner_verify": "UNAVAILABLE: JDK required"}
    cert = subprocess.run(["keytool", "-printcert", "-jarfile", str(apk_path)],
                          text=True, capture_output=True, timeout=30)
    match = re.search(r"SHA256:\s*([0-9A-Fa-f:]+)", cert.stdout)
    digest = match.group(1).upper() if match else None
    verify = subprocess.run(["jarsigner", "-verify", str(apk_path)],
                            text=True, capture_output=True, timeout=45)
    combined = (verify.stdout + "\n" + verify.stderr).lower()
    if verify.returncode != 0:
        status = "FAIL"
    elif "jar verified" in combined:
        status = "PASS"
    else:
        status = "NOT_CONFIRMED_BY_JARSIGNER"
    return {"signer_fingerprint": digest, "jarsigner_verify": status,
            "jarsigner_exit_code": verify.returncode,
            "certificate_extraction": "PASS" if digest else "FAIL_OR_NO_V1_CERT"}


def _inspect_single_apk(apk_path: pathlib.Path, entry_name: str | None = None) -> dict[str, Any]:
    with zipfile.ZipFile(apk_path) as zf:
        bad = zf.testzip()
        if bad:
            raise ValueError(f"APK CRC failure: {bad}")
        if "AndroidManifest.xml" not in zf.namelist():
            raise ValueError("AndroidManifest.xml absent")
        identity = decode_manifest_identity(zf.read("AndroidManifest.xml"))
        names = zf.namelist()
        native = [n for n in names if n.startswith("lib/") and n.endswith(".so")]
    return {"entry_name": entry_name or apk_path.name, "size_bytes": apk_path.stat().st_size,
            "sha256": hashlib.sha256(apk_path.read_bytes()).hexdigest(), **identity,
            "zip_crc": "PASS", "entry_count": len(names), "native_library_count": len(native),
            **_run_signing_tools(apk_path)}


def inspect_package(path: pathlib.Path) -> dict[str, Any]:
    path = path.resolve()
    archive_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if path.suffix.lower() == ".apk":
        apk = _inspect_single_apk(path)
        return {"artifact": path.name, "artifact_type": "apk", "size_bytes": path.stat().st_size,
                "sha256": archive_hash, "package_id": apk["package_id"], "version_name": apk["version_name"],
                "outer_zip_crc": "PASS", "split_count": 1, "all_splits_same_package": True,
                "all_splits_same_signer": bool(apk["signer_fingerprint"]),
                "split_manifest_package_ids": [apk["package_id"]],
                "signer_fingerprints": [apk["signer_fingerprint"]] if apk["signer_fingerprint"] else [],
                "apks": [apk]}
    if path.suffix.lower() != ".xapk":
        raise ValueError("input must be .apk or .xapk")
    with zipfile.ZipFile(path) as zf:
        bad = zf.testzip()
        if bad:
            raise ValueError(f"XAPK CRC failure: {bad}")
        if "manifest.json" not in zf.namelist():
            raise ValueError("XAPK manifest.json absent")
        manifest = json.loads(zf.read("manifest.json"))
        entries = manifest.get("split_apks")
        if not isinstance(entries, list) or not entries:
            raise ValueError("XAPK manifest has no split_apks array")
        declared_package = manifest.get("package_name")
        apks: list[dict[str, Any]] = []
        with tempfile.TemporaryDirectory(prefix="dq-preflight-v56-") as td:
            root = pathlib.Path(td)
            for idx, item in enumerate(entries):
                name = item.get("file") if isinstance(item, dict) else None
                if not isinstance(name, str) or name not in zf.namelist():
                    raise ValueError(f"XAPK split[{idx}] missing or invalid: {name!r}")
                tmp = root / f"split-{idx}.apk"
                tmp.write_bytes(zf.read(name))
                apks.append(_inspect_single_apk(tmp, entry_name=name))
    package_ids = {x["package_id"] for x in apks}
    all_signers = [x["signer_fingerprint"] for x in apks]
    signers = {x for x in all_signers if x}
    return {"artifact": path.name, "artifact_type": "xapk", "size_bytes": path.stat().st_size,
            "sha256": archive_hash, "package_id": declared_package,
            "version_name": manifest.get("version_name"), "manifest_split_count": len(entries),
            "outer_zip_crc": "PASS", "split_count": len(apks),
            "all_splits_same_package": len(package_ids) == 1 and next(iter(package_ids), None) == declared_package,
            "split_manifest_package_ids": sorted(package_ids),
            "all_splits_same_signer": len(signers) == 1 and all(x is not None for x in all_signers),
            "signer_fingerprints": sorted(signers), "apks": apks}


def classify_update(stock: dict[str, Any], candidate: dict[str, Any]) -> str:
    stock_package, candidate_package = stock.get("package_id"), candidate.get("package_id")
    if not stock_package or not candidate_package:
        return "UNKNOWN_PACKAGE_ID"
    if stock_package != candidate_package:
        return "SEPARATE_INSTALL_ID_POSSIBLE_RUNTIME_UNVERIFIED"
    stock_signers = stock.get("signer_fingerprints")
    candidate_signers = candidate.get("signer_fingerprints")
    if not stock_signers or not candidate_signers:
        return "UNKNOWN_SIGNER_IDENTITY"
    if set(stock_signers) != set(candidate_signers):
        return "IN_PLACE_UPDATE_REJECTED_SIGNATURE_MISMATCH_EXPECTED"
    return "SIGNATURE_IDENTITY_COMPATIBLE_OTHER_INSTALL_GATES_UNCHECKED"


def compare(stock_path: pathlib.Path, candidate_path: pathlib.Path) -> dict[str, Any]:
    stock, candidate = inspect_package(stock_path), inspect_package(candidate_path)
    assessment = classify_update(stock, candidate)
    if assessment == "IN_PLACE_UPDATE_REJECTED_SIGNATURE_MISMATCH_EXPECTED":
        note = ("Same package ID but different signer certificate. If the official app is already installed, "
                "Android is expected to reject an in-place update; use a separate package ID for a diagnostic build. "
                "Do not uninstall the official app or treat this as an APK parse failure.")
    elif assessment == "SEPARATE_INSTALL_ID_POSSIBLE_RUNTIME_UNVERIFIED":
        note = "Package IDs differ; side-by-side installation may be possible, but install and runtime remain unverified."
    else:
        note = "This check covers only package ID and signer identity, not all PackageManager/runtime requirements."

    def summary(pkg: dict[str, Any]) -> dict[str, Any]:
        keys = ("artifact", "artifact_type", "size_bytes", "sha256", "package_id", "version_name",
                "manifest_split_count", "outer_zip_crc", "split_count", "all_splits_same_package",
                "all_splits_same_signer", "split_manifest_package_ids", "signer_fingerprints")
        return {key: pkg.get(key) for key in keys}
    return {"schema": "dq-install-preflight-v56", "stock": summary(stock), "candidate": summary(candidate),
            "assessment": assessment, "note": note,
            "limits": ["keytool/jarsigner cover the JAR/v1 verification path, not APK Signature Scheme v2/v3.",
                       "A matching signer does not prove install, launch, HUD, gameplay, or save behavior.",
                       "Do not publish runtime status without device/emulator evidence."]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stock", type=pathlib.Path, required=True, help="original installed-build APK or XAPK")
    parser.add_argument("--candidate", type=pathlib.Path, required=True, help="candidate APK or XAPK")
    parser.add_argument("--output", type=pathlib.Path, help="optional JSON output; refuses to overwrite")
    args = parser.parse_args()
    try:
        report = compare(args.stock, args.candidate)
        rendered = json.dumps(report, indent=2, ensure_ascii=False) + "\n"
        if args.output:
            if args.output.exists():
                raise FileExistsError(f"refusing to overwrite {args.output}")
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        print(rendered, end="")
        return 0
    except (OSError, ValueError, zipfile.BadZipFile, json.JSONDecodeError, subprocess.SubprocessError) as exc:
        print(json.dumps({"schema": "dq-install-preflight-v56", "status": "FAIL", "error": str(exc)}, indent=2))
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
