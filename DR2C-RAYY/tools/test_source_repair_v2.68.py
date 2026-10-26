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
    (root / "assets/deathforth/boot.df").write_text(
        ': id-name-localize ( name -- localized-name )\n'
        '\tdup "fitness" $= if drop "fisik" exit then\n', encoding="utf-8")
    (root / "assets/deathforth/paul/camping-region.df").write_text(
        "uses paul/camping-tent-events.df\n", encoding="utf-8")
    image = Image.new("RGB", (1672, 941), (20, 20, 20))
    ImageDraw.Draw(image).rectangle((23, 837, 334, 890), fill=(1, 10, 16), outline=(0, 225, 245), width=2)
    image.save(root / "assets/gfx/ui/vorenyx_title_screen.png")
    run = subprocess.run([sys.executable, str(script), "--root", str(root)], text=True, capture_output=True)
    if run.returncode:
        print(run.stdout); print(run.stderr, file=sys.stderr); raise SystemExit(run.returncode)
    assert '"fitness" $= if drop "bugar" exit then' in (root / "assets/deathforth/boot.df").read_text()
    assert "load? paul/camping-tent-events.df" in (root / "assets/deathforth/paul/camping-region.df").read_text()
    assert (root / "assets/deathforth/boot.df.bak.v2.68").is_file()
    assert (root / "assets/deathforth/paul/camping-region.df.bak.v2.68").is_file()
    with Image.open(root / "assets/gfx/ui/vorenyx_title_screen.png") as im:
        assert im.size == (1672, 941)
        im.verify()
    run2 = subprocess.run([sys.executable, str(script), "--root", str(root)], text=True, capture_output=True)
    assert run2.returncode == 0, run2.stderr
print("PASS: source edits, backup creation, PNG validation and second-run idempotency")
print("LIMIT: synthetic fixture only; no Deathforth compile or Android runtime test")
