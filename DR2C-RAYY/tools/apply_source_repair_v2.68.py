#!/usr/bin/env python3
"""Apply DR2C VORENYX v2.68 source repairs to a fully overlaid source root.

Root must directly contain assets/deathforth/ and assets/gfx/.
Creates *.bak.v2.68 backups by default. Requires Pillow for the title asset.
"""
from __future__ import annotations
import argparse
from io import BytesIO
from pathlib import Path
import os, shutil, sys
from PIL import Image, ImageDraw, ImageFont

OLD_ALIAS = 'dup "fitness" $= if drop "fisik" exit then'
NEW_ALIAS = 'dup "fitness" $= if drop "bugar" exit then'
OLD_INC = 'uses paul/camping-tent-events.df'
NEW_INC = 'load? paul/camping-tent-events.df'
LABEL = "LOKALISASI INDONESIA // VORENYX"
BG, FG = (1, 10, 16), (128, 248, 255)
FONTS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/system/fonts/Roboto-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

def replace_once(text: str, old: str, new: str, label: str) -> str:
    if text.count(new) == 1 and old not in text:
        return text
    if text.count(old) != 1:
        raise ValueError(f"{label}: expected one old pattern or one already-fixed pattern")
    return text.replace(old, new, 1)

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", required=True, type=Path,
                    help="source root directly containing assets/")
    ap.add_argument("--no-backup", action="store_true")
    args = ap.parse_args()
    root = args.root.resolve()
    paths = {
        "boot": root / "assets/deathforth/boot.df",
        "camping": root / "assets/deathforth/paul/camping-region.df",
        "title": root / "assets/gfx/ui/vorenyx_title_screen.png",
    }
    missing = [str(p) for p in paths.values() if not p.is_file()]
    if missing:
        ap.error("target(s) missing; apply prior source overlays first:\n  " + "\n  ".join(missing))

    boot0 = paths["boot"].read_text(encoding="utf-8")
    camp0 = paths["camping"].read_text(encoding="utf-8")
    boot1 = replace_once(boot0, OLD_ALIAS, NEW_ALIAS, "boot.df")
    if camp0.lower().count(NEW_INC) == 1 and OLD_INC not in camp0.lower():
        camp1 = camp0
    else:
        if camp0.lower().count(OLD_INC) != 1:
            raise ValueError("camping-region.df: expected one mandatory camping-tent-events include")
        i = camp0.lower().index(OLD_INC)
        camp1 = camp0[:i] + NEW_INC + camp0[i + len(OLD_INC):]

    font_path = next((p for p in FONTS if Path(p).is_file()), None)
    if font_path is None:
        raise RuntimeError("No supported bold font found; copy the prepared overlay PNG instead")
    with Image.open(paths["title"]) as src:
        image = src.convert("RGB")
    if image.size != (1672, 941):
        raise ValueError(f"Unexpected title dimensions {image.size}; refusing rewrite")
    draw = ImageDraw.Draw(image)
    draw.rectangle((29, 844, 329, 878), fill=BG)
    font = ImageFont.truetype(font_path, 15)
    if draw.textlength(LABEL, font=font) > 292:
        raise ValueError("Title label does not fit banner")
    draw.text((34, 849), LABEL, font=font, fill=FG, stroke_width=1, stroke_fill=(0, 0, 0))
    b = BytesIO()
    image.save(b, format="PNG", optimize=True)
    image_bytes = b.getvalue()
    with Image.open(BytesIO(image_bytes)) as check:
        check.verify()

    changes = {paths["boot"]: boot1.encode(), paths["camping"]: camp1.encode(), paths["title"]: image_bytes}
    if not args.no_backup:
        for path in changes:
            backup = path.with_name(path.name + ".bak.v2.68")
            if not backup.exists():
                shutil.copy2(path, backup)
    staged = []
    try:
        for path, payload in changes.items():
            tmp = path.with_name(path.name + ".tmp.v2.68")
            tmp.write_bytes(payload)
            staged.append((tmp, path))
        for tmp, path in staged:
            os.replace(tmp, path)
    except Exception:
        for tmp, _ in staged:
            try: tmp.unlink(missing_ok=True)
            except OSError: pass
        raise
    print("PASS: v2.68 source repairs applied; source-only, not an APK.")
    print("Unverified: install, Start runtime, gameplay, save/load.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
