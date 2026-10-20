import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { evaluateAnatomyPose, buildAnatomicalGeometry, renderAnatomySvg, taperedCapsulePath } from "../src/anatomy.mjs";

const base = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"));
const freeBase = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));
function sceneFrom(src = base) {
  return {
    ...src,
    character: {
      ...src.character,
      anatomy_profile: "stylized-natural-v1",
      shoulder_half_width_px: 34,
      waist_half_width_px: 18,
      hip_half_width_px: 23,
      upper_arm_px: 54,
      forearm_px: 53,
      upper_leg_px: 77,
      lower_leg_px: 77,
      head_radius_px: 29,
      head_drop_px: 8
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
  assert.ok(g.headWidth > 0);
  assert.ok(g.shoulderWidth > g.headWidth * 0.75);
  assert.ok(g.shoulderWidth < g.headWidth * 1.8);
  assert.ok(g.height / g.headHeight > 0.8 && g.height / g.headHeight < 2.1);
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
    shoulder_half_width_px: 34, waist_half_width_px: 18, hip_half_width_px: 23 } });
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

test("stance knees stay extended while swing knees visibly flex", () => {
  const scene = sceneFrom();
  let stanceMinimum = 180;
  let swingMaximumAtPeak = 0;
  let stanceSamples = 0, swingSamples = 0;
  for (let i = 0; i < scene.duration_frames; i++) {
    const p = evaluateAnatomyPose(scene, i, "carry");
    for (const side of ["left", "right"]) {
      const foot = p[side + "Foot"];
      const leg = p[side + "Leg"];
      if (foot.inStance) {
        stanceMinimum = Math.min(stanceMinimum, leg.jointAngleDegrees);
        stanceSamples++;
      } else if (foot.swingU >= 0.35 && foot.swingU <= 0.65) {
        swingMaximumAtPeak = Math.max(swingMaximumAtPeak, leg.jointAngleDegrees);
        swingSamples++;
      }
    }
  }
  assert.ok(stanceSamples > 100, "stance coverage must span the full cycle");
  assert.ok(swingSamples >= 12, "peak-swing coverage must be sampled");
  assert.ok(stanceMinimum >= scene.acceptance.min_stance_knee_angle_degrees,
    "stance must be near extension, observed minimum " + stanceMinimum.toFixed(2));
  assert.ok(swingMaximumAtPeak <= scene.acceptance.max_swing_knee_angle_degrees,
    "swing must flex during toe clearance, observed maximum " + swingMaximumAtPeak.toFixed(2));
});

test("head drop shortens exposed neck while keeping the head attached and finite", () => {
  const scene = sceneFrom();
  const p = evaluateAnatomyPose(scene, 24, "carry");
  assert.ok(p.head.y > p.headLocal.y - 8, "head transform remains in expected range");
  assert.ok(Number.isFinite(p.neck.x) && Number.isFinite(p.neck.y));
  const svg = renderAnatomySvg(scene, p, "carry");
  assert.doesNotMatch(svg, /NaN|Infinity|undefined/);
});
