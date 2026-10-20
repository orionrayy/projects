import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {evaluateLocomotion} from "../src/locomotion.mjs";

const scenes = [
  ["carry", JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"))],
  ["free", JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"))]
];

test("gait eases into and out of travel without breaking stance-foot planting", () => {
  for (const [mode, scene] of scenes) {
    const pose = frame => evaluateLocomotion(scene, frame, mode);
    const rootStep = frame => Math.abs(pose(frame + 1).rootX - pose(frame).rootX);
    const firstStep = rootStep(0), cruiseStep = rootStep(80), lastStep = rootStep(scene.duration_frames - 2);
    assert.ok(firstStep < cruiseStep * 0.15, JSON.stringify({firstStep, cruiseStep, lastStep}));
    assert.ok(lastStep < cruiseStep * 0.15, JSON.stringify({firstStep, cruiseStep, lastStep}));
    assert.ok(pose(scene.duration_frames - 1).rootX - pose(0).rootX > 220);
    let maxPlantDrift = 0, plantedPairs = 0;
    for (let f = 1; f < scene.duration_frames; f++) {
      const a = pose(f - 1), b = pose(f);
      for (const side of ["left", "right"]) {
        if (a[side + "Foot"].inStance && b[side + "Foot"].inStance) {
          maxPlantDrift = Math.max(maxPlantDrift, Math.abs(a[side + "Foot"].x - b[side + "Foot"].x));
          plantedPairs++;
        }
      }
    }
    assert.ok(plantedPairs > 100);
    assert.ok(maxPlantDrift < 1e-8, "foot drift during eased stance: " + maxPlantDrift);
  }
});

test("landing response is phase-coupled and has a distinct mid-stance state", () => {
  for (const [mode, scene] of scenes) {
    let contactPose = null, midStancePose = null;
    for (let f = 0; f < scene.duration_frames; f++) {
      const p = evaluateLocomotion(scene, f, mode);
      if (!contactPose || p.diagnostics.contactLoad > contactPose.diagnostics.contactLoad) contactPose = p;
      if (p.cyclePhase > 0.22 && p.cyclePhase < 0.28 &&
          (!midStancePose || p.diagnostics.contactLoad < midStancePose.diagnostics.contactLoad)) midStancePose = p;
    }
    assert.ok(contactPose.diagnostics.contactLoad > 0.95);
    assert.ok(midStancePose);
    assert.ok(midStancePose.diagnostics.contactLoad < contactPose.diagnostics.contactLoad * 0.3);
    assert.ok(Math.abs(contactPose.diagnostics.contactBalance) > 0.7);
    assert.ok(Number.isFinite(contactPose.torsoAngle) && Number.isFinite(contactPose.headAngle));
  }
});

test("small gait-cycle variation is deterministic, bounded, and not a repeated identical loop", () => {
  for (const [mode, scene] of scenes) {
    const samples = [];
    for (let f = 0; f < scene.duration_frames; f++) {
      const p = evaluateLocomotion(scene, f, mode);
      assert.ok(Math.abs(p.cycleVariation) <= 1.001);
      samples.push(p.cycleVariation);
    }
    const rounded = samples.map(x => x.toFixed(4));
    assert.ok(new Set(rounded).size > 20, "variation should evolve smoothly between cycles");
    assert.equal(evaluateLocomotion(scene, 40, mode).cycleVariation, evaluateLocomotion(scene, 40, mode).cycleVariation);
  }
});
