#!/usr/bin/env python3
"""Safe fixture test for apply_source_repair_v2.68.py."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess, sys
from PIL import Image, ImageDraw

script = Path(__file__).with_name("apply_source_repair_v2.68.py")
with TemporaryDirectory(prefix="dr2c_v268_") as tmp:
    root = Path(tmp)
    (root / "assets/deathforth/paul").mkdir(parents=True)
    (root / "assets/gfx/ui").mkdir(parents=True)
    (root / "res/drawable-xxhdpi-v4").mkdir(parents=True)
    (root / "assets/deathforth/boot.df").write_text(
        ': id-name-localize ( name -- localized-name )\n'
        '\tdup "fitness" $= if drop "fisik" exit then\n', encoding="utf-8")
    (root / "assets/deathforth/paul/camping-region.df").write_text(
        "uses paul/camping-tent-events.df\n", encoding="utf-8")
    image = Image.new("RGB", (1672, 941), (20, 20, 20))
    ImageDraw.Draw(image).rectangle((23, 837, 334, 890), fill=(1, 10, 16), outline=(0, 225, 245), width=2)
    image.save(root / "assets/gfx/ui/vorenyx_title_screen.png")
    splash = Image.new("RGB", (2560, 1600), (20, 20, 20))
    ImageDraw.Draw(splash).rectangle((30, 1481, 530, 1526), fill=(3, 16, 24), outline=(0, 225, 245), width=2)
    splash.save(root / "res/drawable-xxhdpi-v4/splash.png")
    run = subprocess.run([sys.executable, str(script), "--root", str(root)], text=True, capture_output=True)
    if run.returncode:
        print(run.stdout); print(run.stderr, file=sys.stderr); raise SystemExit(run.returncode)
    boot = (root / "assets/deathforth/boot.df").read_text(encoding="utf-8")
    camp = (root / "assets/deathforth/paul/camping-region.df").read_text(encoding="utf-8")
    assert 'dup "fitness" $= if drop "bugar" exit then' in boot
    assert "load? paul/camping-tent-events.df" in camp
    for target in [
        root / "assets/deathforth/boot.df",
        root / "assets/deathforth/paul/camping-region.df",
        root / "assets/gfx/ui/vorenyx_title_screen.png",
        root / "res/drawable-xxhdpi-v4/splash.png",
    ]:
        assert target.with_name(target.name + ".bak.v2.68").is_file(), f"backup missing for {target}"
    with Image.open(root / "assets/gfx/ui/vorenyx_title_screen.png") as im:
        assert im.size == (1672, 941); im.verify()
    with Image.open(root / "res/drawable-xxhdpi-v4/splash.png") as im:
        assert im.size == (2560, 1600); im.verify()
    # Idempotency: second run is allowed and must not fail.
    run2 = subprocess.run([sys.executable, str(script), "--root", str(root)], text=True, capture_output=True)
    assert run2.returncode == 0, run2.stderr
print("PASS: fixture, source edits, four backups, PNG validation and repeat application")
print("LIMIT: synthetic fixture only; no Deathforth compiler or Android runtime test")
