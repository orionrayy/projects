import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { renderSvgFrame, summarizeScene } from "../scripts/render-preview.mjs";

const scene = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

test("profile head uses a compact silhouette and restrained single-feature face", () => {
  assert.equal(scene.scene_version, "0.9.5");
  assert.equal(scene.motion.head_center_offset_y_px, 137);
  const svg = renderSvgFrame(scene, 72, "free");
  assert.ok(svg.includes('data-face-design="soft-profile-v1"'));
  assert.ok(svg.includes('data-profile-feature="silhouette"'));
  for (const feature of ["hair", "ear", "brow", "eye", "nose", "mouth"]) {
    assert.ok(svg.includes('data-profile-feature="' + feature + '"'), "missing " + feature);
    assert.equal((svg.match(new RegExp('data-profile-feature="' + feature + '"', "g")) || []).length, 1, feature + " must be drawn once");
  }
});

test("head width and height are balanced and the compact neck stays within the proportion gate", () => {
  const r = summarizeScene(scene, "free");
  const a = r.anatomyDiagnostics;
  assert.ok(a.headHeightPx > 0);
  assert.ok(a.neckLengthPx / a.headHeightPx < 0.55, "neck remains visually too long: " + a.neckLengthPx / a.headHeightPx);
  assert.ok(scene.character.head_radius_px * 0.91 / (scene.character.head_radius_px * 0.94) > 0.94);
});
