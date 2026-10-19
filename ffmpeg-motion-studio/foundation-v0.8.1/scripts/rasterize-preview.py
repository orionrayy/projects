import argparse
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw
import cairosvg

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("output", nargs="?", default="dist")
    args = ap.parse_args()
    root = Path(args.output).resolve()
    svg_root = root / "svg"
    png_root = root / "png"
    profiles = ["carry", "free"]
    for profile in profiles:
        svgs = sorted((svg_root / profile).glob("frame-*.svg"))
        if len(svgs) != 192:
            raise SystemExit(f"{profile}: expected 192 SVG frames, found {len(svgs)}")
        target = png_root / profile
        target.mkdir(parents=True, exist_ok=True)
        for svg in svgs:
            out = target / (svg.stem + ".png")
            cairosvg.svg2png(url=str(svg), write_to=str(out), output_width=1280, output_height=720)
            with Image.open(out) as im:
                if im.size != (1280, 720):
                    raise SystemExit(f"bad raster dimensions: {out} {im.size}")
        mp4 = root / f"motion-studio-v0.8.1-anatomy-{profile}.mp4"
        cmd = [
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-framerate", "24", "-i", str(target / "frame-%04d.png"),
            "-frames:v", "192", "-c:v", "libx264", "-preset", "medium",
            "-crf", "18", "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(mp4)
        ]
        subprocess.run(cmd, check=True, timeout=180)
        thumbs = []
        for i in range(0, 192, 24):
            with Image.open(target / f"frame-{i:04d}.png") as im:
                thumb = im.convert("RGB")
                thumb.thumbnail((320, 180))
                thumbs.append((i, thumb.copy()))
        sheet = Image.new("RGB", (4 * 320, 3 * 210), "#f2f0e9")
        draw = ImageDraw.Draw(sheet)
        for n, (frame, thumb) in enumerate(thumbs):
            x, y = (n % 4) * 320, (n // 4) * 210
            sheet.paste(thumb, (x, y + 22))
            draw.text((x + 8, y + 4), f"{profile} | frame {frame}", fill="#182329")
        sheet.save(root / f"anatomy-contact-sheet-{profile}.jpg", quality=90)
        print(f"{profile}: {len(svgs)} SVG + PNG frames; wrote {mp4}")
if __name__ == "__main__":
    main()
