import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { evaluateLocomotion, sampleStanceWorldDrift } from "../src/locomotion.mjs";

const scene = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"));
const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);

test("locomotion is deterministic for random-access frames", () => {
  assert.deepEqual(evaluateLocomotion(scene, 57), evaluateLocomotion(scene, 57));
  assert.deepEqual(evaluateLocomotion(scene, 0), evaluateLocomotion(scene, 0));
});

test("left/right gait phases stay half a cycle apart", () => {
  for (let i = 0; i < scene.duration_frames; i += 7) {
    const s = evaluateLocomotion(scene, i);
    assert.ok(Math.abs(Math.abs(s.leftFoot.phase - s.rightFoot.phase) - 0.5) < 1e-8);
  }
});

test("all frames satisfy geometry and prop-contact limits", () => {
  for (let i = 0; i < scene.duration_frames; i += 1) {
    const s = evaluateLocomotion(scene, i);
    assert.ok(s.diagnostics.boneLengthErrorPx <= scene.acceptance.max_bone_length_error_px);
    assert.ok(s.diagnostics.ankleClampErrorPx <= 0.02);
    assert.ok(s.diagnostics.basketContactErrorPx <= scene.acceptance.max_basket_contact_error_px);
    assert.ok(s.diagnostics.groundPenetrationPx <= scene.acceptance.max_ground_penetration_px);
  }
});

test("planted stance foot has bounded world drift", () => {
  for (let i = 0; i < scene.duration_frames; i += 2) {
    const s = evaluateLocomotion(scene, i);
    for (const side of ["left", "right"]) {
      if (!s[side + "Foot"].inStance) continue;
      const drift = sampleStanceWorldDrift(scene, i, side, 9);
      assert.notEqual(drift, null);
      assert.ok(drift <= scene.acceptance.max_stance_foot_drift_px);
    }
  }
});

test("limb step changes remain inside the declared gates", () => {
  let elbowNear = 0, elbowFar = 0, kneeNear = 0, kneeFar = 0;
  for (let i = 1; i < scene.duration_frames; i += 1) {
    const a = evaluateLocomotion(scene, i - 1);
    const b = evaluateLocomotion(scene, i);
    elbowNear = Math.max(elbowNear, dist(a.nearArm.elbow, b.nearArm.elbow));
    elbowFar = Math.max(elbowFar, dist(a.farArm.elbow, b.farArm.elbow));
    kneeNear = Math.max(kneeNear, dist(a.leftLeg.knee, b.leftLeg.knee));
    kneeFar = Math.max(kneeFar, dist(a.rightLeg.knee, b.rightLeg.knee));
  }
  assert.ok(elbowNear <= scene.acceptance.max_arm_elbow_step_px);
  assert.ok(elbowFar <= scene.acceptance.max_arm_elbow_step_px);
  assert.ok(kneeNear <= scene.acceptance.max_knee_step_px);
  assert.ok(kneeFar <= scene.acceptance.max_knee_step_px);
});

test("invalid frame indexes fail closed", () => {
  assert.throws(() => evaluateLocomotion(scene, -1), RangeError);
  assert.throws(() => evaluateLocomotion(scene, scene.duration_frames), RangeError);
  assert.throws(() => evaluateLocomotion(scene, 0.5), RangeError);
});
