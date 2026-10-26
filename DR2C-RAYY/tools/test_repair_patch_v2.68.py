#!/usr/bin/env python3
"""Static regression checks for DR2C VORENYX source repair patch v2.68."""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
boot = (ROOT / "overlay/assets/deathforth/boot.df").read_text(encoding="utf-8")
camping = (ROOT / "overlay/assets/deathforth/paul/camping-region.df").read_text(encoding="utf-8")
title_path = ROOT / "overlay/assets/gfx/ui/vorenyx_title_screen.png"
splash_path = ROOT / "overlay/res/drawable-xxhdpi-v4/splash.png"

assert boot.count('dup "fitness" $= if drop "bugar" exit then') == 1, "fitness alias not aligned"
assert 'dup "fitness" $= if drop "fisik" exit then' not in boot, "old alias remains"
assert camping.count('load? paul/camping-tent-events.df') == 1, "missing include not made optional"
assert 'uses paul/camping-tent-events.df' not in camping.lower(), "hard include remains"

assert title_path.is_file(), "title image missing"
with Image.open(title_path) as im:
    assert im.size == (1672, 941), f"unexpected title image dimensions: {im.size}"
    rgb = im.convert("RGB")
    for y in range(866, 878):
        for x in range(30, 329):
            assert rgb.getpixel((x,y)) == (1,10,16), f"leftover title pixels at {(x,y)}"

assert splash_path.is_file(), "Android splash image missing"
with Image.open(splash_path) as im:
    assert im.size == (2560, 1600), f"unexpected splash image dimensions: {im.size}"
    rgb = im.convert("RGB")
    for y in range(1515, 1520):
        for x in range(44, 522):
            assert rgb.getpixel((x,y)) == (3,16,24), f"leftover splash pixels at {(x,y)}"

print("PASS: aliases, optional include, title artwork, splash artwork and dimensions/cleanup")
print("LIMIT: static checks only; no full language parser, APK build, install or runtime test")
