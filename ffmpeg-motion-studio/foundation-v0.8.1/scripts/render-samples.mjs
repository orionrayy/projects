import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { evaluateAnatomyPose, buildAnatomicalGeometry, renderAnatomySvg } from "../src/anatomy.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(here, "..");
const base = path.resolve(root, "..", "foundation-v0.8.0");
const output = path.resolve(process.argv[2] || path.join(root, "dist"));
const profiles = [
  { name: "carry", mode: "carry", file: "locomotion-lab.json" },
  { name: "free", mode: "free", file: "locomotion-free.json" }
];
const manifest = {
  version: "0.8.1",
  renderer: "Motion Studio procedural anatomy SVG",
  created_at: new Date().toISOString(),
  profiles: {},
  acceptance: { finite_geometry: true, frame_count: 0, max_contact_error_px: 0 }
};
for (const item of profiles) {
  const scene = JSON.parse(fs.readFileSync(path.join(base, "scenes", item.file), "utf8"));
  scene.character = {
    ...scene.character,
    anatomy_profile: "stylized-natural-v1",
    shoulder_half_width_px: 27.5,
    waist_half_width_px: 17,
    hip_half_width_px: 23
  };
  const dir = path.join(output, "svg", item.name);
  fs.mkdirSync(dir, { recursive: true });
  const rows = [];
  for (let frame = 0; frame < scene.duration_frames; frame++) {
    const pose = evaluateAnatomyPose(scene, frame, item.mode);
    const geometry = buildAnatomicalGeometry(scene, pose);
    const svg = renderAnatomySvg(scene, pose, item.mode);
    if (/NaN|Infinity|undefined/.test(svg)) throw new Error("Non-finite render at " + item.name + " frame " + frame);
    fs.writeFileSync(path.join(dir, "frame-" + String(frame).padStart(4, "0") + ".svg"), svg);
    rows.push({
      frame, time_seconds: pose.timeSeconds,
      bone_length_error_px: pose.diagnostics.boneLengthErrorPx,
      contact_error_px: pose.diagnostics.basketContactErrorPx,
      ground_penetration_px: pose.diagnostics.groundPenetrationPx,
      torso_height_px: geometry.height,
      head_height_px: geometry.headHeight,
      shoulder_width_px: geometry.shoulderWidth,
      head_width_px: geometry.headWidth,
      torso_to_head_height_ratio: geometry.height / geometry.headHeight
    });
  }
  const maxContact = Math.max(...rows.map(r => r.contact_error_px));
  manifest.profiles[item.name] = {
    scene: item.file, mode: item.mode, fps: scene.fps,
    width: scene.canvas.width, height: scene.canvas.height,
    frame_count: rows.length, duration_seconds: rows.length / scene.fps,
    max_contact_error_px: maxContact,
    min_torso_to_head_height_ratio: Math.min(...rows.map(r => r.torso_to_head_height_ratio)),
    max_torso_to_head_height_ratio: Math.max(...rows.map(r => r.torso_to_head_height_ratio)),
    frames: rows
  };
  manifest.acceptance.frame_count += rows.length;
  manifest.acceptance.max_contact_error_px = Math.max(manifest.acceptance.max_contact_error_px, maxContact);
}
fs.mkdirSync(output, { recursive: true });
fs.writeFileSync(path.join(output, "anatomy-manifest.json"), JSON.stringify(manifest, null, 2) + "\n");
console.log(JSON.stringify({
  output, total_frames: manifest.acceptance.frame_count,
  profiles: Object.fromEntries(Object.entries(manifest.profiles).map(([k, v]) => [k, {
    frames: v.frame_count, fps: v.fps, resolution: v.width + "x" + v.height,
    max_contact_error_px: v.max_contact_error_px
  }]))
}, null, 2));
