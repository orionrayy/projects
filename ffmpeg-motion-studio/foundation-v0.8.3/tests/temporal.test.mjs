import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {summarizeScene} from "../scripts/render-preview.mjs";

const carry = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"));
const free = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

test("frame-step and acceleration metrics are finite and bounded", () => {
  for (const [scene, mode] of [[carry,"carry"],[free,"free"]]) {
    const report = summarizeScene(scene,mode);
    const t = report.temporalDiagnostics;
    assert.equal(t.allTemporalMetricsFinite,true);
    assert.ok(t.maxHeadStepPx < 6, "head step spikes");
    assert.ok(t.maxNearElbowStepPx < 14, "near elbow step spikes");
    assert.ok(t.maxFarElbowStepPx < 14, "far elbow step spikes");
    assert.ok(t.maxNearWristStepPx < 18, "near wrist step spikes");
    assert.ok(t.maxFarWristStepPx < 18, "far wrist step spikes");
    assert.ok(t.maxKneeStepPx < 18, "knee step spikes");
    assert.ok(t.maxJointAccelerationPxPerFrame2 < 8, "joint acceleration spikes");
    assert.ok(t.stanceFootSamplePairs > 100, "insufficient stance samples to support drift metric");
    assert.ok(t.stanceTransitions > 10, "contact-state transitions were not sampled");
  }
});

test("planted stance feet do not slide between consecutive stance frames", () => {
  for (const [scene,mode] of [[carry,"carry"],[free,"free"]]) {
    const t = summarizeScene(scene,mode).temporalDiagnostics;
    assert.ok(t.maxStanceFootDriftPerFramePx < 0.05, "stance drift exceeds tolerance: "+t.maxStanceFootDriftPerFramePx);
  }
});
