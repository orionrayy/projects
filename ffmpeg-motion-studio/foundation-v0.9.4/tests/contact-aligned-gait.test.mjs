import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { evaluateLocomotion } from "../src/locomotion.mjs";
import { summarizeScene } from "../scripts/render-preview.mjs";
import { summarizeReferenceVisualSequence } from "../scripts/render-reference-visual-preview.mjs";

const scenes = [
  ["carry", JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"))],
  ["free", JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"))]
];

function assertContactBoundary(pose, floorY, label) {
  assert.equal(pose.diagnostics.stance.left, true, label + " left foot is not in stance");
  assert.equal(pose.diagnostics.stance.right, true, label + " right foot is not in stance");
  assert.ok(Math.abs(pose.leftFoot.y - floorY) < 1e-8, label + " left foot misses ground");
  assert.ok(Math.abs(pose.rightFoot.y - floorY) < 1e-8, label + " right foot misses ground");
  assert.ok(Math.abs(pose.cycleCoordinate - pose.baseCycleCoordinate) < 1e-8, label + " phase warp shifted a cycle boundary");
}

test("opening and final rendered frames land in two-foot contact", () => {
  for (const [mode, scene] of scenes) {
    const first = evaluateLocomotion(scene, 0, mode);
    const lastIndex = scene.duration_frames - 1;
    const last = evaluateLocomotion(scene, lastIndex, mode);
    const floorY = scene.background.horizon_y;
    assertContactBoundary(first, floorY, mode + " first frame");
    assertContactBoundary(last, floorY, mode + " final frame");
    assert.ok(Math.abs(last.gaitRateCyclesPerSecond) < 1e-8, mode + " terminal gait speed must settle to zero");
    const previous = evaluateLocomotion(scene, lastIndex - 1, mode);
    assert.ok(Math.abs(last.rootX - previous.rootX) < 0.05, mode + " terminal root motion did not decelerate");
  }
});

test("longer-stride profiles remain within existing geometry and temporal gates", () => {
  for (const [mode, scene] of scenes) {
    const report = summarizeScene(scene, mode);
    assert.ok(report.motionEnvelopeDiagnostics.strideLengthPx >= 92, mode + " stride regressed: " + report.motionEnvelopeDiagnostics.strideLengthPx);
    assert.ok(report.temporalDiagnostics.maxKneeStepPx < 13, mode + " knee displacement exceeded the existing limit: " + report.temporalDiagnostics.maxKneeStepPx);
    assert.ok(report.maxAnkleClampErrorPx < 1.5, mode + " ankle reach exceeded the existing limit: " + report.maxAnkleClampErrorPx);
    assert.ok(report.temporalDiagnostics.maxStanceFootDriftPerFramePx < 0.05, mode + " stance foot slipped");
  }
});

test("integrated portrait gait settles on grounded feet at both render boundaries", () => {
  const gait = summarizeReferenceVisualSequence().portraitGaitDiagnostics;
  for (const label of ["first", "last"]) {
    const p = gait.startEndContact[label];
    assert.equal(p.leftInStance, true, "portrait " + label + " left foot is not in stance");
    assert.equal(p.rightInStance, true, "portrait " + label + " right foot is not in stance");
    assert.ok(p.leftGroundErrorPx < 1e-8 && p.rightGroundErrorPx < 1e-8, "portrait " + label + " feet do not meet the floor");
    assert.ok(p.phaseBoundaryErrorCycles < 1e-8, "portrait " + label + " phase boundary drifted");
  }
  assert.ok(Math.abs(gait.startEndContact.last.gaitRateCyclesPerSecond) < 1e-8, "portrait final gait must settle to zero speed");
  assert.ok(gait.effectiveStridePx >= 95, "portrait stride must not regress");
  assert.ok(gait.maxKneeStepPx < 13, "portrait knee step must stay within its existing gate");
});
