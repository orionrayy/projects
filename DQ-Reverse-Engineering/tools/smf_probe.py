#!/usr/bin/env python3
"""Read-only probe for a binary SMF pack; does not decode or decrypt it."""
import argparse, collections, hashlib, json, math
from pathlib import Path

MAGICS = {
    b"PK\x03\x04": "ZIP", b"\x1f\x8b": "GZIP", b"BZh": "BZIP2",
    b"\xfd7zXZ\x00": "XZ", b"7z\xbc\xaf\x27\x1c": "7-Zip",
    b"Rar!": "RAR", b"\x28\xb5\x2f\xfd": "Zstandard",
    b"\x04\x22\x4d\x18": "LZ4-frame", b"SQLite format 3\x00": "SQLite",
    b"UnityFS": "UnityFS",
}

def entropy(data):
    if not data: return 0.0
    counts = collections.Counter(data); n = len(data)
    return -sum((v/n)*math.log2(v/n) for v in counts.values())

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input", type=Path)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--max-text-runs", type=int, default=100)
    args = ap.parse_args()
    data = args.input.read_bytes()
    runs, start = [], None
    for i, b in enumerate(data + b"\x00"):
        if 32 <= b <= 126 or b in (9, 10, 13):
            if start is None: start = i
        else:
            if start is not None and i-start >= 6:
                runs.append({"offset": start, "text": data[start:i].decode("ascii", "replace")})
            start = None
    hits = []
    for magic, name in MAGICS.items():
        p = 0
        while True:
            p = data.find(magic, p)
            if p < 0: break
            hits.append({"offset": p, "format": name, "magic_hex": magic.hex()})
            p += 1
            if len(hits) >= 2000: break
    result = {
        "file": args.input.name, "size_bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(), "header_hex": data[:64].hex(" "),
        "entropy_bits_per_byte": round(entropy(data), 6),
        "byte_values_present": len(set(data)), "known_magic_hits": hits[:2000],
        "printable_ascii_runs": runs[:args.max_text_runs],
        "interpretation": "Heuristic only: high entropy/no known signatures can indicate compression, encryption, or a proprietary format; this does not distinguish them."
    }
    rendered = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output: args.output.write_text(rendered + "\n", encoding="utf-8")
    print(rendered)

if __name__ == "__main__": main()
