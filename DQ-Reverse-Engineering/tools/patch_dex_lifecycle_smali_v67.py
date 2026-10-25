#!/usr/bin/env python3
"""Fail-closed source-only smali overlay for the side-effect-free v67 ABI probe."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path

PINNED_DEX_SHA256 = "bcfe58e6380c9360128b474e80c8744f955ad998dfa9863424a662190f27fe6b"
RENDERER = Path("com/shinybox/smash/S3DRenderer.smali")
PROBE = Path("com/shinybox/smash/DqNativeProbe.smali")
DRAW = "onDrawFrame(Ljavax/microedition/khronos/opengles/GL10;)V"
SHUTDOWN = "onShutdown()V"
INIT_CALL = re.compile(r"^\\s*invoke-[^\\s]+\\s+\\{[^}]*\\},\\s*Lcom/shinybox/smash/S3DRenderer;->engineInitialize\\(\\)Z(?:\\s+#.*)?$")
STOP_CALL = re.compile(r"^\\s*invoke-[^\\s]+\\s+\\{[^}]*\\},\\s*Lcom/shinybox/smash/S3DRenderer;->engineShutdown\\(\\)V(?:\\s+#.*)?$")
INIT_FIELD = re.compile(r"^\\s*iput-boolean\\s+(v\\d+),\\s*[^,]+,\\s*[^,]+->bInitialized:Z(?:\\s+#.*)?$")
SKIP_DIRECTIVES = (".line ", ".local ", ".end local ", ".restart local ", ".prologue", ".epilogue", ".param ", ".end param")

PROBE_SMALI = """.class public final Lcom/shinybox/smash/DqNativeProbe;
.super Ljava/lang/Object;
.field private static sLibraryLoaded:Z
.field private static sRegistered:Z

.method private constructor <init>()V
    .locals 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public static declared-synchronized tryRegisterAndRoundTrip()V
    .locals 1
    sget-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sLibraryLoaded:Z
    if-nez v0, :probe_library_ready
    :probe_load_start
    const-string v0, "dqbridge"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    :probe_load_end
    const/4 v0, 0x1
    sput-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sLibraryLoaded:Z
    goto :probe_library_ready
    :probe_load_failed
    move-exception v0
    const/4 v0, 0x0
    sput-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sLibraryLoaded:Z
    return-void
    .catch Ljava/lang/Throwable; {:probe_load_start .. :probe_load_end} :probe_load_failed
    :probe_library_ready
    sget-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sRegistered:Z
    if-nez v0, :probe_invoke
    :probe_register_start
    invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->nativeRegisterProbe()Z
    move-result v0
    if-eqz v0, :probe_register_end
    const/4 v0, 0x1
    sput-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sRegistered:Z
    :probe_invoke
    invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->nativeInvokeProbe()Z
    move-result v0
    if-nez v0, :probe_register_end
    invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->tryUnregister()V
    :probe_register_end
    return-void
    :probe_register_failed
    move-exception v0
    invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->tryUnregister()V
    return-void
    .catch Ljava/lang/Throwable; {:probe_register_start .. :probe_register_end} :probe_register_failed
.end method

.method public static declared-synchronized tryUnregister()V
    .locals 1
    sget-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sLibraryLoaded:Z
    if-eqz v0, :probe_unregister_return
    sget-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sRegistered:Z
    if-eqz v0, :probe_unregister_return
    :probe_unregister_start
    invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->nativeUnregisterProbe()Z
    move-result v0
    if-eqz v0, :probe_unregister_end
    const/4 v0, 0x0
    sput-boolean v0, Lcom/shinybox/smash/DqNativeProbe;->sRegistered:Z
    :probe_unregister_end
    return-void
    :probe_unregister_failed
    move-exception v0
    return-void
    .catch Ljava/lang/Throwable; {:probe_unregister_start .. :probe_unregister_end} :probe_unregister_failed
    :probe_unregister_return
    return-void
.end method

.method public static native nativeRegisterProbe()Z
.end method
.method public static native nativeInvokeProbe()Z
.end method
.method public static native nativeUnregisterProbe()Z
.end method
"""

class PatchError(ValueError):
    pass

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def method_bounds(lines: list[str], descriptor: str) -> tuple[int, int]:
    starts = [i for i, line in enumerate(lines) if line.lstrip().startswith(".method ") and descriptor in line]
    if len(starts) != 1:
        raise PatchError(f"expected exactly one method {descriptor}; found {len(starts)}")
    start = starts[0]
    ends = [i for i in range(start + 1, len(lines)) if lines[i].strip() == ".end method"]
    if not ends:
        raise PatchError(f"unterminated method {descriptor}")
    return start, ends[0]

def next_instruction(lines: list[str], start: int, end: int) -> int:
    for i in range(start, end):
        s = lines[i].strip()
        if not s or s.startswith("#") or s.startswith(":") or s.startswith("."):
            continue
        if s.startswith(SKIP_DIRECTIVES):
            continue
        return i
    raise PatchError("expected next instruction, reached method end")

def patch_renderer(source: str) -> tuple[str, dict]:
    if "Lcom/shinybox/smash/DqNativeProbe;->" in source:
        raise PatchError("renderer already references DqNativeProbe; refusing double patch")
    lines = source.splitlines(keepends=True)
    start, end = method_bounds(lines, DRAW)
    calls = [i for i in range(start + 1, end) if INIT_CALL.match(lines[i].rstrip("\r\n"))]
    if len(calls) != 1:
        raise PatchError(f"expected exactly one engineInitialize()Z call; found {len(calls)}")
    idx = calls[0]
    next_idx = next_instruction(lines, idx + 1, end)
    field = INIT_FIELD.match(lines[next_idx].rstrip("\r\n"))
    if not field:
        raise PatchError("init shape changed: engineInitialize()Z must be followed by original bInitialized iput")
    reg = field.group(1)
    nl = "\r\n" if lines[idx].endswith("\r\n") else "\n"
    indent = re.match(r"^\\s*", lines[idx]).group(0)
    injected = [
        f"{indent}move-result {reg}{nl}",
        f"{indent}if-eqz {reg}, :dq_probe_init_skip_v67{nl}",
        f"{indent}invoke-static {{}}, Lcom/shinybox/smash/DqNativeProbe;->tryRegisterAndRoundTrip()V{nl}",
        f":dq_probe_init_skip_v67{nl}",
        f"{indent}const/4 {reg}, 0x1{nl}",
    ]
    lines[idx + 1:idx + 1] = injected
    reports = {"result_register": reg, "probe_only_on_true_result": True, "original_initialized_flag_semantics_preserved": True}
    for descriptor in (DRAW, SHUTDOWN):
        a, b = method_bounds(lines, descriptor)
        stops = [i for i in range(a + 1, b) if STOP_CALL.match(lines[i].rstrip("\r\n"))]
        if len(stops) != 1:
            raise PatchError(f"expected exactly one engineShutdown()V in {descriptor}; found {len(stops)}")
        n = stops[0]
        if n > a + 1 and "DqNativeProbe;->tryUnregister()V" in lines[n-1]:
            raise PatchError(f"unregister hook already present in {descriptor}")
        nl = "\r\n" if lines[n].endswith("\r\n") else "\n"
        indent = re.match(r"^\\s*", lines[n]).group(0)
        lines.insert(n, f"{indent}invoke-static {{}}, Lcom/shinybox/smash/DqNativeProbe;->tryUnregister()V{nl}")
    output = "".join(lines)
    out_lines = output.splitlines()
    a, b = method_bounds(out_lines, DRAW)
    block = out_lines[a:b+1]
    init = next(i for i, line in enumerate(block) if INIT_CALL.match(line))
    seq = [s.strip() for s in block[init:init+6]]
    expected = [seq[0], f"move-result {reg}", f"if-eqz {reg}, :dq_probe_init_skip_v67", "invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->tryRegisterAndRoundTrip()V", ":dq_probe_init_skip_v67", f"const/4 {reg}, 0x1"]
    if seq != expected:
        raise PatchError("post-patch init gate/order mismatch")
    for descriptor in (DRAW, SHUTDOWN):
        a, b = method_bounds(out_lines, descriptor)
        block = out_lines[a:b+1]
        n = next(i for i, line in enumerate(block) if STOP_CALL.match(line))
        if block[n-1].strip() != "invoke-static {}, Lcom/shinybox/smash/DqNativeProbe;->tryUnregister()V":
            raise PatchError(f"unregister is not immediately before shutdown in {descriptor}")
    return output, {"result_register": reg, **reports, "unregister_before_shutdown": True, "runtime_status": "NOT_VERIFIED", "catalog_routes_assigned": 0, "runtime_verified_catalog_effects": 0}

def create_overlay(source_root: Path, output_root: Path, source_dex: Path) -> dict:
    source_root, output_root = source_root.resolve(), output_root.resolve()
    if not source_root.is_dir() or not source_dex.is_file():
        raise PatchError("source root or source DEX missing")
    dex_hash = sha(source_dex.read_bytes())
    if dex_hash != PINNED_DEX_SHA256:
        raise PatchError(f"source DEX hash mismatch: expected {PINNED_DEX_SHA256}, got {dex_hash}")
    if output_root.exists():
        raise PatchError(f"refusing overwrite: {output_root}")
    if output_root == source_root or source_root in output_root.parents:
        raise PatchError("output root must be separate and outside source root")
    renderer = source_root / RENDERER
    if not renderer.is_file():
        raise PatchError(f"renderer missing: {renderer}")
    probe = source_root / PROBE
    if probe.exists():
        raise PatchError(f"probe class already exists in source tree: {probe}")
    before = renderer.read_bytes()
    patched, patch_report = patch_renderer(before.decode("utf-8"))
    shutil.copytree(source_root, output_root)
    out_renderer = output_root / RENDERER
    out_renderer.write_text(patched, encoding="utf-8", newline="")
    out_probe = output_root / PROBE
    out_probe.parent.mkdir(parents=True, exist_ok=True)
    out_probe.write_text(PROBE_SMALI, encoding="utf-8", newline="")
    report = {"schema":"dq.dex-lifecycle-smali-patch.v67","source_dex_sha256":dex_hash,"source_renderer_sha256":sha(before),"patched_renderer_sha256":sha(out_renderer.read_bytes()),"probe_class_sha256":sha(out_probe.read_bytes()),"apk_or_dex_bytes_written":False,"dex_assembly_performed":False,"apk_or_xapk_built":False,**patch_report}
    (output_root / "dq-lifecycle-smali-patch-v67.json").write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    return report

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source-root",type=Path,required=True)
    ap.add_argument("--output-root",type=Path,required=True)
    ap.add_argument("--source-dex",type=Path,required=True)
    args=ap.parse_args()
    try:
        report=create_overlay(args.source_root,args.output_root,args.source_dex)
    except (OSError,PatchError) as exc:
        print(json.dumps({"status":"FAIL","error":str(exc)},indent=2))
        return 2
    print(json.dumps({"status":"SOURCE_OVERLAY_CREATED",**report},indent=2))
    print("Source smali overlay only. No game DEX/APK/XAPK assembled or runtime-tested.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
