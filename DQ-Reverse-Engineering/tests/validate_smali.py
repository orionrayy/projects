#!/usr/bin/env python3
"""Static consistency checks for Smali-like source; this does not assemble files."""
from pathlib import Path
import argparse, collections, json, re, sys

def validate(root: Path):
    files = sorted(root.rglob("*.smali"))
    errors = []
    totals = collections.Counter()
    for path in files:
        text = path.read_text(encoding="utf-8")
        if text.count(".method ") != text.count(".end method"):
            errors.append(f"{path}: unmatched method boundaries")
        if text.count(".class ") != 1:
            errors.append(f"{path}: expected one .class directive")
        for method in re.finditer(r"(?ms)^\.method ([^\n]+)\n(.*?)(?=^\.end method\s*$)", text):
            signature, body = method.group(1), method.group(2)
            totals["methods"] += 1
            regs = re.search(r"(?m)^\s*\.registers (\d+)\s*$", body)
            units = re.search(r"code_units=(\d+)", body)
            spans = []
            for line in body.splitlines():
                payload = re.search(r"dex_pc=0x([0-9a-fA-F]+); payload_units=(\d+)", line)
                if payload:
                    spans.append((int(payload.group(1),16), int(payload.group(2)), "payload"))
                    totals["payloads"] += 1
                    continue
                raw = re.search(r"dex_pc=0x([0-9a-fA-F]+); raw=([0-9a-fA-F ]+)", line)
                if raw:
                    spans.append((int(raw.group(1),16), len(raw.group(2).split()), "instruction"))
                    totals["instructions"] += 1
            if units:
                expected = int(units.group(1)); cursor = 0
                for pc, width, kind in sorted(spans):
                    if pc != cursor:
                        errors.append(f"{path.name}:{signature}: {kind} begins at 0x{pc:x}, expected 0x{cursor:x}")
                        break
                    if width < 1:
                        errors.append(f"{path.name}:{signature}: zero-width {kind}")
                        break
                    cursor += width
                if cursor != expected:
                    errors.append(f"{path.name}:{signature}: coverage {cursor}/{expected} code units")
            if regs:
                count = int(regs.group(1))
                for line in body.splitlines():
                    if "dex_pc=" not in line and not re.match(r"\s*\.(catch|catchall|packed-switch|sparse-switch|array-data|end|registers)", line):
                        continue
                    code = line.split("#", 1)[0]
                    for register in re.findall(r"\bv(\d+)\b", code):
                        if int(register) >= count:
                            errors.append(f"{path.name}:{signature}: v{register} exceeds .registers {count}")
                            break
            labels = set(re.findall(r"(?m)^\s*(:L_[0-9a-fA-F]+)\s*$", body))
            references = set(re.findall(r":L_[0-9a-fA-F]+", "\n".join(line.split("#", 1)[0] for line in body.splitlines())))
            if references - labels:
                errors.append(f"{path.name}:{signature}: undefined labels {sorted(references-labels)}")
            if any(marker in body for marker in ("opcode-0x", "method_handle@", "call_site@", "<decode-error", "Linvalid/")):
                errors.append(f"{path.name}:{signature}: unresolved placeholder")
    return {"files":len(files),"methods":totals["methods"],"instructions":totals["instructions"],
            "payloads":totals["payloads"],"errors":len(errors),"error_examples":errors[:100]}

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]/"disassembly")
    args=parser.parse_args(); result=validate(args.root)
    print(json.dumps(result,indent=2)); sys.exit(1 if result["errors"] else 0)

if __name__=="__main__": main()
