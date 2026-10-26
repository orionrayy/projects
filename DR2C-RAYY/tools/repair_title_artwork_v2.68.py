#!/usr/bin/env python3
"""Remove stale numeric version labels from VORENYX title/splash artwork.

Usage: python repair_title_artwork_v2.68.py input.png output.png
Image is selected by dimensions: 1672x941 title art or 2560x1600 splash.
Requires Pillow. Prefer the prepared overlay PNGs where available.
"""
from __future__ import annotations
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

LABEL = "LOKALISASI INDONESIA // VORENYX"
FONTS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",
    "/system/fonts/Roboto-Bold.ttf",
    "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
)

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"input image not found: {args.input}")
    font_path = next((p for p in FONTS if Path(p).is_file()), None)
    if font_path is None:
        parser.error("no compatible bold sans font found; use the supplied patched PNG")
    with Image.open(args.input) as source:
        image = source.convert("RGB")
    draw = ImageDraw.Draw(image)
    if image.size == (1672, 941):
        clear_box, bg, fg, font_size, y, max_width = (29, 844, 329, 878), (1, 10, 16), (128, 248, 255), 15, 849, 292
        x = 34
        draw.rectangle(clear_box, fill=bg)
        font = ImageFont.truetype(font_path, font_size)
        if draw.textlength(LABEL, font=font) > max_width:
            parser.error("title label does not fit in banner")
        draw.text((x, y), LABEL, font=font, fill=fg, stroke_width=1, stroke_fill=(0, 0, 0))
    elif image.size == (2560, 1600):
        clear_box, bg, fg = (44, 1485, 521, 1520), (3, 16, 24), (177, 249, 255)
        font = ImageFont.truetype(font_path, 24)
        draw.rectangle(clear_box, fill=bg)
        width = draw.textlength(LABEL, font=font)
        if width > (clear_box[2] - clear_box[0] - 12):
            parser.error("splash label does not fit in banner")
        x = round((clear_box[0] + clear_box[2] - width) / 2)
        draw.text((x, 1487), LABEL, font=font, fill=fg)
    else:
        parser.error(f"unsupported dimensions {image.size}; expected 1672x941 or 2560x1600")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, format="PNG", optimize=True)
    with Image.open(args.output) as check:
        check.verify()
    print(f"Wrote {args.output} ({image.width}x{image.height})")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
