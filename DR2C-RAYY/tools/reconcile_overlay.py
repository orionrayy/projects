#!/usr/bin/env python3
"""Validate and reconcile ordered Deathforth source-overlay ZIPs; never builds an APK."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Any

ESCAPED_QUOTE = bytes((0x5C, 0x22))


class ReconcileError(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def checked_zip(path: Path) -> tuple[zipfile.ZipFile, list[str]]:
    if not path.is_file():
        raise ReconcileError(f'file not found: {path}')
    try:
        z = zipfile.ZipFile(path, 'r')
    except (OSError, zipfile.BadZipFile) as e:
        raise ReconcileError(f'invalid ZIP {path.name}: {e}') from e
    names = z.namelist()
    duplicates = [n for n, c in Counter(names).items() if c > 1]
    if duplicates:
        z.close()
        raise ReconcileError(f'duplicate paths in {path.name}: {duplicates[:10]}')
    bad = z.testzip()
    if bad:
        z.close()
        raise ReconcileError(f'CRC failure in {path.name}: {bad}')
    return z, names


def safe_path(raw: str, archive: str) -> str:
    if '\\' in raw:
        raise ReconcileError(f'backslash path in {archive}: {raw}')
    p = PurePosixPath(raw)
    if p.is_absolute() or not p.parts or any(x in ('', '.', '..') for x in p.parts) or ':' in p.parts[0]:
        raise ReconcileError(f'unsafe overlay path in {archive}: {raw}')
    return p.as_posix()


def read_overlay(path: Path) -> dict[str, bytes]:
    z, names = checked_zip(path)
    payload: dict[str, bytes] = {}
    try:
        for name in names:
            if name.endswith('/'):
                continue
            parts = PurePosixPath(name).parts
            if 'overlay' not in parts:
                continue
            i = parts.index('overlay')
            if i == len(parts) - 1:
                continue
            logical = safe_path(PurePosixPath(*parts[i + 1:]).as_posix(), path.name)
            if logical in payload:
                raise ReconcileError(f'duplicate logical overlay path in {path.name}: {logical}')
            payload[logical] = z.read(name)
    finally:
        z.close()
    if not payload:
        raise ReconcileError(f'no overlay payload found in {path.name}')
    return payload


def source_index(names: list[str]) -> tuple[str, dict[str, str]]:
    candidates = [n for n in names if '/assets/deathforth/' in n]
    if not candidates:
        raise ReconcileError('source ZIP has no assets/deathforth tree')
    prefix = Counter(n.split('assets/deathforth/', 1)[0] for n in candidates).most_common(1)[0][0]
    mapping = {n[len(prefix):]: n for n in names if not n.endswith('/') and n.startswith(prefix) and n[len(prefix):]}
    if 'assets/deathforth/boot.df' not in mapping:
        raise ReconcileError('cannot resolve source root: assets/deathforth/boot.df missing')
    return prefix, mapping


def mask_strings_and_comments(text: str) -> tuple[str, bool]:
    """Mask display strings and // comments without changing code positions.

    Deathforth source in this project does not support C/JSON-style escaped quote
    sequences inside display strings. Those are rejected separately before this
    lexer is used. Returns (masked source, has_unclosed_string).
    """
    out = list(text)
    i = 0
    in_string = False
    while i < len(text):
        if in_string:
            if text[i] == '"':
                out[i] = ' '
                in_string = False
                i += 1
                continue
            if text[i] not in '\r\n':
                out[i] = ' '
            i += 1
            continue
        if text[i:i + 2] == '//':
            while i < len(text) and text[i] not in '\r\n':
                out[i] = ' '
                i += 1
            continue
        if text[i] == '"':
            out[i] = ' '
            in_string = True
        i += 1
    return ''.join(out), in_string


def single_quoted_symbol_stream(text: str) -> tuple[list[str], bool]:
    """Return the ordered stream of Forth-style single-quoted symbols."""
    masked, unclosed = mask_strings_and_comments(text)
    return re.findall(r"'\s*([A-Za-z_][A-Za-z0-9_-]*)", masked), unclosed


def reconcile(base: Path, patches: list[Path], out: Path, report_path: Path,
              expected_base_sha256: str | None = None, fail_on_overrides: bool = False) -> dict[str, Any]:
    base_hash = sha256_file(base)
    if expected_base_sha256 and base_hash.lower() != expected_base_sha256.lower():
        raise ReconcileError(f'base SHA-256 mismatch: expected {expected_base_sha256.lower()}, got {base_hash}')
    bz, base_names = checked_zip(base)
    try:
        prefix, source_paths = source_index(base_names)
        source_data = {logical: bz.read(zip_path) for logical, zip_path in source_paths.items()}
    finally:
        bz.close()
    effective = dict(source_data)
    final: dict[str, bytes] = {}
    history: dict[str, list[str]] = {}
    layers, input_reports = [], [{
        'role': 'base_source_archive', 'file': base.name, 'bytes': base.stat().st_size,
        'sha256': base_hash, 'zip_entries': len(source_data), 'source_prefix': prefix,
    }]
    for order, patch in enumerate(patches, 1):
        payload = read_overlay(patch)
        overrides, added, missing = [], [], []
        for logical, content in sorted(payload.items()):
            if logical in final:
                overrides.append(logical)
            if logical not in source_paths:
                if logical.endswith('.df'):
                    missing.append(logical)
                else:
                    added.append(logical)
            final[logical] = content
            history.setdefault(logical, []).append(patch.name)
            if logical.endswith('.df'):
                effective[logical] = content
        if missing:
            raise ReconcileError(f'overlay scripts missing from base in {patch.name}: {missing[:10]}')
        if fail_on_overrides and overrides:
            raise ReconcileError(f'overrides forbidden in {patch.name}: {overrides[:10]}')
        digest = sha256_file(patch)
        layers.append({'order': order, 'file': patch.name, 'bytes': patch.stat().st_size,
                       'sha256': digest, 'payload_count': len(payload),
                       'overridden_paths': overrides, 'added_non_script_paths': added})
        input_reports.append({'role': f'overlay_layer_{order}', 'file': patch.name,
                              'bytes': patch.stat().st_size, 'sha256': digest,
                              'payload_count': len(payload)})

    boot = effective.get('assets/deathforth/boot.df', b'')
    marker_ok = b'"GAME-MARKER" $anew' in boot and b'"PENANDA-GAME" $anew' not in boot
    escaped_quote_files = sorted(p for p, b in effective.items() if p.startswith('assets/deathforth/') and p.endswith('.df') and ESCAPED_QUOTE in b)
    source_df_count = sum(1 for p in source_data if p.startswith('assets/deathforth/') and p.endswith('.df'))
    overlay_df_paths = sorted(p for p in final if p.startswith('assets/deathforth/') and p.endswith('.df'))
    overlay_df_count = len(overlay_df_paths)

    unclosed_quote_files = []
    for path, payload in final.items():
        if path.startswith('assets/deathforth/') and path.endswith('.df'):
            _, unclosed = mask_strings_and_comments(payload.decode('utf-8', 'replace'))
            if unclosed:
                unclosed_quote_files.append(path)

    symbol_stream_differences = []
    for path in overlay_df_paths:
        before = source_data.get(path)
        after = final[path]
        if before is None:
            continue
        old_symbols, old_unclosed = single_quoted_symbol_stream(before.decode('utf-8', 'replace'))
        new_symbols, new_unclosed = single_quoted_symbol_stream(after.decode('utf-8', 'replace'))
        if old_unclosed or new_unclosed or old_symbols != new_symbols:
            first_difference = next((i for i, pair in enumerate(zip(old_symbols, new_symbols)) if pair[0] != pair[1]), min(len(old_symbols), len(new_symbols)))
            symbol_stream_differences.append({
                'path': path,
                'source_symbol_count': len(old_symbols),
                'overlay_symbol_count': len(new_symbols),
                'first_difference_index': first_difference,
                'source_window': old_symbols[max(0, first_difference - 2):first_difference + 3],
                'overlay_window': new_symbols[max(0, first_difference - 2):first_difference + 3],
            })

    perkdef = effective.get('assets/deathforth/perkdef.df', b'')
    canonical_perk_key_ok = b'"Jack of All Trades" $perk' in perkdef and b'"Serba Bisa" $perk' not in perkdef

    required_contracts = {
        'assets/deathforth/events.df': [b'main-event-do-select'],
        'assets/deathforth/game-select.df': [b'main-event-do-select', b'select-start', b'select-boot'],
        'assets/deathforth/events/tutorial.df': [b'tutorchat-1'],
    }
    missing_contracts = []
    for path, needles in required_contracts.items():
        payload = effective.get(path, b'')
        for needle in needles:
            if needle not in payload:
                missing_contracts.append({'path': path, 'required_token': needle.decode('ascii')})

    if not marker_ok:
        raise ReconcileError('canonical GAME-MARKER invariant failed')
    if escaped_quote_files:
        raise ReconcileError(f'escaped backslash-quote remains in .df files: {escaped_quote_files[:10]}')
    if unclosed_quote_files:
        raise ReconcileError(f'unclosed display string detected in overlay .df files: {unclosed_quote_files[:10]}')
    if symbol_stream_differences:
        raise ReconcileError(f'overlay changed single-quoted code-symbol sequence: {symbol_stream_differences[:5]}')
    if not canonical_perk_key_ok:
        raise ReconcileError('canonical perk data key "Jack of All Trades" was altered')
    if missing_contracts:
        raise ReconcileError(f'critical Start/tutorial dispatch contract missing: {missing_contracts}')

    manifest: dict[str, Any] = {
        'project': 'DR2C VORENYX',
        'artifact_type': 'normalized cumulative source overlay patch; NOT an APK',
        'inputs': input_reports,
        'layers': layers,
        'layer_order_is_significant': True,
        'final_overlay': {
            'unique_paths': len(final), 'deathforth_df_files': overlay_df_count,
            'path_sha256': {p: hashlib.sha256(b).hexdigest() for p, b in sorted(final.items())},
            'override_history': {p: h for p, h in sorted(history.items()) if len(h) > 1},
        },
        'checks': {
            'input_zip_crc': 'PASS',
            'duplicate_input_paths': 0,
            'all_overlay_df_paths_resolve_to_source': True,
            'canonical_boot_marker': 'PASS',
            'escaped_backslash_quote_files': escaped_quote_files,
            'closed_display_strings_all_overlay_df_files': 'PASS',
            'single_quoted_code_symbol_sequences_preserved': 'PASS',
            'single_quoted_code_symbol_sequence_differences': symbol_stream_differences,
            'canonical_perk_data_key': 'PASS',
            'critical_start_tutorial_dispatch_contracts': 'PASS',
            'missing_critical_contracts': missing_contracts,
            'source_df_files_detected': source_df_count,
            'overlay_df_files_after_reconciliation': overlay_df_count,
            'global_localization_coverage': 'NOT COMPUTED',
            'deathforth_full_parse': 'NOT RUN',
            'apk_build': 'NOT PERFORMED',
            'android_runtime': 'NOT TESTED',
            'save_load_test': 'NOT TESTED',
        },
        'limitations': [
            'Only the supplied patch layers are included; missing newer patch ZIPs must not be inferred from documentation.',
            'This tool creates a source patch, not an APK; it does not sign, align, install, or runtime-test Android packages.',
            'A local signing key cannot update an installation signed by a different certificate.',
        ],
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for logical, content in sorted(final.items()):
            z.writestr(f'overlay/{logical}', content)
        z.writestr('audit/reconciliation_manifest.json', json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')
        z.writestr('README_RECONCILED_SOURCE_PATCH.md',
                   '# DR2C VORENYX reconciled source overlay\n\nSource patch only. Not built, signed, installed or runtime-tested.\n')
    oz, output_names = checked_zip(out)
    oz.close()
    manifest['output'] = {'file': out.name, 'bytes': out.stat().st_size, 'sha256': sha256_file(out),
                          'zip_entries': len(output_names), 'zip_crc': 'PASS',
                          'duplicate_paths': [n for n, c in Counter(output_names).items() if c > 1]}
    if manifest['output']['duplicate_paths']:
        raise ReconcileError('duplicate paths in generated output')
    report_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return manifest


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--base-source', required=True, type=Path)
    p.add_argument('--patch', action='append', required=True, type=Path, help='repeat in application order')
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--report', required=True, type=Path)
    p.add_argument('--expected-base-sha256')
    p.add_argument('--fail-on-overrides', action='store_true')
    a = p.parse_args(argv)
    try:
        r = reconcile(a.base_source, a.patch, a.out, a.report, a.expected_base_sha256, a.fail_on_overrides)
    except (ReconcileError, OSError, ValueError) as e:
        print(json.dumps({'status': 'FAIL', 'error': str(e)}, indent=2), file=sys.stderr)
        return 2
    print(json.dumps({
        'status': 'PASS',
        'output': r['output'],
        'overlay_paths': r['final_overlay']['unique_paths'],
        'overrides': sum(len(x['overridden_paths']) for x in r['layers']),
        'source_df_files': r['checks']['source_df_files_detected'],
        'overlay_df_files': r['checks']['overlay_df_files_after_reconciliation'],
        'boot_marker': r['checks']['canonical_boot_marker'],
        'escaped_quote_scan': 'PASS' if not r['checks']['escaped_backslash_quote_files'] else 'FAIL',
        'closed_string_scan': r['checks']['closed_display_strings_all_overlay_df_files'],
        'code_symbol_contract': r['checks']['single_quoted_code_symbol_sequences_preserved'],
        'perk_key_contract': r['checks']['canonical_perk_data_key'],
        'start_dispatch_contract': r['checks']['critical_start_tutorial_dispatch_contracts'],
        'apk_build': r['checks']['apk_build'],
        'android_runtime': r['checks']['android_runtime'],
    }, indent=2))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
