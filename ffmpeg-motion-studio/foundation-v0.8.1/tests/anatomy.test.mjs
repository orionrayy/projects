import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { evaluateAnatomyPose, buildAnatomicalGeometry, renderAnatomySvg, taperedCapsulePath } from "../src/anatomy.mjs";

const base = JSON.parse(fs.readFileSync(new URL("../../foundation-v0.8.0/scenes/locomotion-lab.json", import.meta.url), "utf8"));
const freeBase = JSON.parse(fs.readFileSync(new URL("../../foundation-v0.8.0/scenes/locomotion-free.json", import.meta.url), "utf8"));
function sceneFrom(src = base) {
  return {
    ...src,
    character: {
      ...src.character,
      anatomy_profile: "stylized-natural-v1",
      shoulder_half_width_px: 27.5,
      waist_half_width_px: 17,
      hip_half_width_px: 23,
      upper_arm_px: 54,
      forearm_px: 53,
      upper_leg_px: 79,
      lower_leg_px: 81,
      head_radius_px: 29
    }
  };
}
const d = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

test("tapered capsules reject invalid input and form rounded, tapered paths", () => {
  const path = taperedCapsulePath({ x: 0, y: 0 }, { x: 0, y: 40 }, 10, 5);
  assert.match(path, /^M /);
  assert.match(path, / Q /);
  assert.match(path, / Z$/);
  assert.throws(() => taperedCapsulePath({ x: 0, y: 0 }, { x: 1, y: 1 }, 0, 3), TypeError);
});

test("anatomical torso geometry stays finite and has plausible stylized proportions", () => {
  const scene = sceneFrom();
  const pose = evaluateAnatomyPose(scene, 0, "carry");
  const g = buildAnatomicalGeometry(scene, pose);
  assert.ok(g.path.startsWith("M "));
  assert.ok(Number.isFinite(g.height) && g.height > 0);
  assert.ok(g.metrics.headWidthPx > 0);
  assert.ok(g.metrics.shoulderWidthPx > g.metrics.headWidthPx * 0.75);
  assert.ok(g.metrics.shoulderWidthPx < g.metrics.headWidthPx * 1.8);
  assert.ok(g.metrics.torsoToHeadHeightRatio > 0.8 && g.metrics.torsoToHeadHeightRatio < 2.1);
});

test("shoulders are distinct and arm IK preserves bone length across every carry frame", () => {
  const scene = sceneFrom();
  for (let i = 0; i < scene.duration_frames; i++) {
    const p = evaluateAnatomyPose(scene, i, "carry");
    assert.ok(d(p.shoulders.near, p.shoulders.far) > 25);
    for (const arm of [p.nearArm, p.farArm]) {
      assert.ok(Math.abs(d(arm.shoulder, arm.elbow) - scene.character.upper_arm_px) < 1e-6);
      assert.ok(Math.abs(d(arm.elbow, arm.wrist) - scene.character.forearm_px) < 1e-6);
    }
    assert.ok(p.diagnostics.basketContactErrorPx < 1e-6);
  }
});

test("free-arm retargeting remains deterministic and finite for all frames", () => {
  const scene = sceneFrom({ ...freeBase, character: { ...freeBase.character, anatomy_profile: "stylized-natural-v1",
    shoulder_half_width_px: 27.5, waist_half_width_px: 17, hip_half_width_px: 23 } });
  for (let i = 0; i < scene.duration_frames; i++) {
    const p = evaluateAnatomyPose(scene, i, "free");
    for (const v of [p.pelvis, p.chest, p.head, p.shoulders.near, p.shoulders.far, p.nearArm.elbow, p.farArm.elbow]) {
      assert.ok(Number.isFinite(v.x) && Number.isFinite(v.y));
    }
  }
  assert.deepEqual(evaluateAnatomyPose(scene, 63, "free"), evaluateAnatomyPose(scene, 63, "free"));
});

test("SVG render contains anatomy shapes and has no non-finite coordinates", () => {
  const scene = sceneFrom();
  const pose = evaluateAnatomyPose(scene, 48, "carry");
  const svg = renderAnatomySvg(scene, pose, "carry");
  assert.match(svg, /<svg/);
  assert.match(svg, /ANATOMY STUDY/);
  assert.match(svg, /<ellipse/);
  assert.match(svg, /<path/);
  assert.doesNotMatch(svg, /NaN|Infinity|undefined/);
});

test("frame bounds and arm-mode validation fail closed", () => {
  const scene = sceneFrom();
  assert.throws(() => evaluateAnatomyPose(scene, -1, "carry"), RangeError);
  assert.throws(() => evaluateAnatomyPose(scene, scene.duration_frames, "carry"), RangeError);
  assert.throws(() => evaluateAnatomyPose(scene, 0, "invalid"), RangeError);
});
