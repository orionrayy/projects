import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path("dist")
def probe(path):
    raw = subprocess.run([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,r_frame_rate,nb_frames",
        "-show_entries", "format=duration", "-of", "json", str(path)
    ], check=True, capture_output=True, text=True, timeout=30)
    data = json.loads(raw.stdout)
    stream = data["streams"][0]
    return {
        "codec": stream.get("codec_name"),
        "width": stream.get("width"),
        "height": stream.get("height"),
        "fps": stream.get("r_frame_rate"),
        "frames": int(stream.get("nb_frames") or 0),
        "duration_seconds": float(data["format"]["duration"]),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size
    }

def main():
    if not (ROOT / "anatomy-manifest.json").exists():
        raise SystemExit("Missing anatomy-manifest.json")
    report = {"version": "0.8.1", "profiles": {}, "status": "PASS"}
    for profile in ("carry", "free"):
        path = ROOT / f"motion-studio-v0.8.1-anatomy-{profile}.mp4"
        if not path.exists():
            raise SystemExit(f"Missing render: {path}")
        item = probe(path)
        failures = []
        if item["codec"] != "h264": failures.append("codec must be h264")
        if (item["width"], item["height"]) != (1280, 720): failures.append("resolution must be 1280x720")
        if item["fps"] != "24/1": failures.append("fps must be 24/1")
        if item["frames"] != 192: failures.append("frame count must be 192")
        if abs(item["duration_seconds"] - 8.0) > 0.05: failures.append("duration must be 8 seconds ±0.05")
        item["failures"] = failures
        report["profiles"][profile] = item
        if failures: report["status"] = "FAIL"
    ROOT.mkdir(parents=True, exist_ok=True)
    (ROOT / "render-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)
if __name__ == "__main__":
    main()
