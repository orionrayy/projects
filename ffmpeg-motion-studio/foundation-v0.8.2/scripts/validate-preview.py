import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path("dist")
MIN_STANCE_ANGLE = 145.0
MAX_PEAK_SWING_ANGLE = 125.0

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

def knee_metrics(frames):
    stance, peak_swing = [], []
    for frame in frames:
        for side in ("left", "right"):
            angle = frame[f"{side}_knee_angle_degrees"]
            if frame[f"{side}_stance"]:
                stance.append(angle)
            elif 0.35 <= frame[f"{side}_swing_u"] <= 0.65:
                peak_swing.append(angle)
    return {
        "stance_samples": len(stance),
        "min_stance_knee_angle_degrees": min(stance) if stance else None,
        "peak_swing_samples": len(peak_swing),
        "max_peak_swing_knee_angle_degrees": max(peak_swing) if peak_swing else None
    }

def orient(a, b, c):
    return (b["x"]-a["x"])*(c["y"]-a["y"]) - (b["y"]-a["y"])*(c["x"]-a["x"])

def proper_cross(a, b, c, d):
    o1, o2 = orient(a, b, c), orient(a, b, d)
    o3, o4 = orient(c, d, a), orient(c, d, b)
    return o1 * o2 < -1e-6 and o3 * o4 < -1e-6

def intersection_metrics(frames):
    leg_crossings = 0
    free_arm_crossings = 0
    for frame in frames:
        left = [(frame["left_hip"], frame["left_knee"]), (frame["left_knee"], frame["left_ankle"])]
        right = [(frame["right_hip"], frame["right_knee"]), (frame["right_knee"], frame["right_ankle"])]
        leg_crossings += sum(proper_cross(a, b, c, d) for (a, b) in left for (c, d) in right)
        near = [(frame["near_arm_shoulder"], frame["near_arm_elbow"]), (frame["near_arm_elbow"], frame["near_arm_wrist"])]
        far = [(frame["far_arm_shoulder"], frame["far_arm_elbow"]), (frame["far_arm_elbow"], frame["far_arm_wrist"])]
        free_arm_crossings += sum(proper_cross(a, b, c, d) for (a, b) in near for (c, d) in far)
    return {"opposite_leg_centerline_crossings": leg_crossings, "free_arm_centerline_crossings": free_arm_crossings}

def main():
    manifest_path = ROOT / "anatomy-manifest.json"
    if not manifest_path.exists():
        raise SystemExit("Missing anatomy-manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    report = {"version": "0.8.2", "profiles": {}, "status": "PASS"}
    for profile in ("carry", "free"):
        path = ROOT / f"motion-studio-v0.8.2-anatomy-{profile}.mp4"
        if not path.exists():
            raise SystemExit(f"Missing render: {path}")
        item = probe(path)
        failures = []
        if item["codec"] != "h264": failures.append("codec must be h264")
        if (item["width"], item["height"]) != (1280, 720): failures.append("resolution must be 1280x720")
        if item["fps"] != "24/1": failures.append("fps must be 24/1")
        if item["frames"] != 192: failures.append("frame count must be 192")
        if abs(item["duration_seconds"] - 8.0) > 0.05: failures.append("duration must be 8 seconds ±0.05")
        frames = manifest.get("profiles", {}).get(profile, {}).get("frames", [])
        if len(frames) != 192:
            failures.append("manifest must cover all 192 frames")
        else:
            knee = knee_metrics(frames)
            intersections = intersection_metrics(frames)
            item.update(knee)
            item.update(intersections)
            if intersections["opposite_leg_centerline_crossings"] != 0:
                failures.append("opposite leg centerlines intersect")
            if profile == "free" and intersections["free_arm_centerline_crossings"] != 0:
                failures.append("free-arm centerlines intersect")
            if knee["stance_samples"] < 100: failures.append("insufficient stance knee samples")
            if knee["min_stance_knee_angle_degrees"] is None or knee["min_stance_knee_angle_degrees"] < MIN_STANCE_ANGLE:
                failures.append(f"minimum stance knee angle must be >= {MIN_STANCE_ANGLE} degrees")
            if knee["peak_swing_samples"] < 12: failures.append("insufficient peak swing knee samples")
            if knee["max_peak_swing_knee_angle_degrees"] is None or knee["max_peak_swing_knee_angle_degrees"] > MAX_PEAK_SWING_ANGLE:
                failures.append(f"maximum peak-swing knee angle must be <= {MAX_PEAK_SWING_ANGLE} degrees")
        sheets = list(ROOT.glob(f"anatomy-contact-sheet-{profile}-*.jpg"))
        item["full_cycle_contact_sheets"] = len(sheets)
        if len(sheets) != 8: failures.append("all eight 24-frame contact sheets must be present")
        item["failures"] = failures
        report["profiles"][profile] = item
        if failures: report["status"] = "FAIL"
    (ROOT / "render-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
    if report["status"] != "PASS":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
