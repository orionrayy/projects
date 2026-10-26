#!/usr/bin/env python3
"""Apply the low-risk DR2C VORENYX v2.68 source and artwork repairs.

The root directory must contain assets/deathforth/, assets/gfx/ and
res/drawable-xxhdpi-v4/splash.png. All targets are validated before writes;
backups are created by default as *.bak.v2.68. This is not an APK builder.
Requires Pillow.
"""
from __future__ import annotations
import argparse
from io import BytesIO
from pathlib import Path
import os
import shutil
import sys
from PIL import Image, ImageDraw, ImageFont

OLD_ALIAS = 'dup "fitness" $= if drop "fisik" exit then'
NEW_ALIAS = 'dup "fitness" $= if drop "bugar" exit then'
OLD_INCLUDE = 'uses paul/camping-tent-events.df'
NEW_INCLUDE = 'load? paul/camping-tent-events.df'
LABEL = "LOKALISASI INDONESIA // VORENYX"
TITLE_BG = (1, 10, 16)
SPLASH_BG = (3, 16, 24)
TITLE_FG = (128, 248, 255)
SPLASH_FG = (177, 249, 255)
FONT_CANDIDATES = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/system/fonts/Roboto-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

def choose_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    raise RuntimeError("No compatible bold font found. Apply the supplied overlay PNG files directly instead.")

def patch_text(content: str, old: str, new: str, what: str) -> str:
    if content.count(new) == 1 and old not in content:
        return content
    if content.count(old) != 1:
        raise ValueError(f"{what}: expected exactly one old pattern or one already-fixed pattern")
    return content.replace(old, new, 1)

def make_artwork(path: Path, expected_size: tuple[int, int]) -> bytes:
    with Image.open(path) as source:
        image = source.convert("RGB")
    if image.size != expected_size:
        raise ValueError(f"{path}: unexpected dimensions {image.size}; expected {expected_size}; refusing to rewrite")
    draw = ImageDraw.Draw(image)
    if expected_size == (1672, 941):
        # Extra title card: preserve its frame and clear the former V2.43 suffix.
        draw.rectangle((29, 844, 329, 878), fill=TITLE_BG)
        font = choose_font(15)
        if draw.textlength(LABEL, font=font) > 292:
            raise ValueError("title label does not fit in banner")
        draw.text((34, 849), LABEL, font=font, fill=TITLE_FG, stroke_width=1, stroke_fill=(0, 0, 0))
    elif expected_size == (2560, 1600):
        # Splash banner is at the lower-left. Clear only its dark interior;
        # the cyan frame at x≈30..530/y≈1481..1526 stays untouched.
        clear_box = (44, 1485, 521, 1520)
        draw.rectangle(clear_box, fill=SPLASH_BG)
        font = choose_font(24)
        width = draw.textlength(LABEL, font=font)
        if width > (clear_box[2] - clear_box[0] - 12):
            raise ValueError("splash label does not fit inside banner")
        x = round((clear_box[0] + clear_box[2] - width) / 2)
        draw.text((x, 1487), LABEL, font=font, fill=SPLASH_FG)
    else:
        raise ValueError(f"unsupported artwork size: {expected_size}")
    stream = BytesIO()
    image.save(stream, format="PNG", optimize=True)
    payload = stream.getvalue()
    with Image.open(BytesIO(payload)) as check:
        check.verify()
    return payload

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="fully overlaid source root; directly contains assets/ and res/")
    parser.add_argument("--no-backup", action="store_true", help="do not write *.bak.v2.68 backups")
    args = parser.parse_args()
    root = args.root.resolve()
    paths = {
        "boot": root / "assets/deathforth/boot.df",
        "camping": root / "assets/deathforth/paul/camping-region.df",
        "title": root / "assets/gfx/ui/vorenyx_title_screen.png",
        "splash": root / "res/drawable-xxhdpi-v4/splash.png",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        parser.error("target file(s) missing; use the fully overlaid source tree:\n  " + "\n  ".join(missing))
    boot_before = paths["boot"].read_text(encoding="utf-8")
    camping_before = paths["camping"].read_text(encoding="utf-8")
    boot_after = patch_text(boot_before, OLD_ALIAS, NEW_ALIAS, "boot.df fitness label")
    if camping_before.lower().count(NEW_INCLUDE) == 1 and OLD_INCLUDE not in camping_before.lower():
        camping_after = camping_before
    else:
        count = camping_before.lower().count(OLD_INCLUDE)
        if count != 1:
            raise ValueError("camping-region.df: expected exactly one mandatory camping-tent-events include")
        idx = camping_before.lower().index(OLD_INCLUDE)
        camping_after = camping_before[:idx] + NEW_INCLUDE + camping_before[idx + len(OLD_INCLUDE):]

    # Generate both images before modifying anything to avoid half-applied repairs.
    title_bytes = make_artwork(paths["title"], (1672, 941))
    splash_bytes = make_artwork(paths["splash"], (2560, 1600))
    replacements = {
        paths["boot"]: boot_after.encode("utf-8"),
        paths["camping"]: camping_after.encode("utf-8"),
        paths["title"]: title_bytes,
        paths["splash"]: splash_bytes,
    }
    if not args.no_backup:
        for path in replacements:
            backup = path.with_name(path.name + ".bak.v2.68")
            if not backup.exists():
                shutil.copy2(path, backup)
    staged = []
    try:
        for path, data in replacements.items():
            tmp = path.with_name(path.name + ".tmp.v2.68")
            tmp.write_bytes(data)
            staged.append((tmp, path))
        for tmp, final in staged:
            os.replace(tmp, final)
    except Exception:
        for tmp, _ in staged:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass
        raise
    print("PASS: v2.68 source and artwork repairs applied")
    print(f"  fitness display label: {'updated' if boot_after != boot_before else 'already aligned'}")
    print(f"  camping include: {'made optional' if camping_after != camping_before else 'already optional'}")
    print("  extra title artwork: version-independent label saved")
    print("  Android splash artwork: version-independent label saved")
    print("NOTE: source-only patch; APK build, signature verification, install and runtime remain untested")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)
