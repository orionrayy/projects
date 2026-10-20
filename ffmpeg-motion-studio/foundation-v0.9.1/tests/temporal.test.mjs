import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {summarizeScene} from "../scripts/render-preview.mjs";
import {footLocalOffset} from "../src/locomotion.mjs";

const carry = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"));
const free = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

test("frame-step and acceleration metrics are finite and bounded", () => {
  for (const [scene, mode] of [[carry,"carry"],[free,"free"]]) {
    const report = summarizeScene(scene,mode);
    const t = report.temporalDiagnostics;
    assert.equal(t.allTemporalMetricsFinite,true);
    assert.ok(t.maxHeadStepPx < 3.5, "head step spikes: " + t.maxHeadStepPx);
    assert.ok(t.maxChestStepPx < 4.2, "chest motion is too active: " + t.maxChestStepPx);
    assert.ok(t.maxNearElbowStepPx < 5.5, "near elbow step spikes: " + t.maxNearElbowStepPx);
    assert.ok(t.maxFarElbowStepPx < 5.5, "far elbow step spikes: " + t.maxFarElbowStepPx);
    assert.ok(t.maxNearWristStepPx < 7.5, "near wrist step spikes: " + t.maxNearWristStepPx);
    assert.ok(t.maxFarWristStepPx < 7.5, "far wrist step spikes: " + t.maxFarWristStepPx);
    assert.ok(t.maxKneeStepPx < 9.5, "knee step spikes: " + t.maxKneeStepPx);
    assert.ok(t.maxFootStepPx < 7.5, "foot step spikes: " + t.maxFootStepPx);
    assert.ok(t.maxJointAccelerationPxPerFrame2 < 5.5, "joint acceleration spikes: " + JSON.stringify(t));
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


test("stance-to-swing foot path is C2-smooth at phase boundaries",()=>{
  const sf=0.6,stride=44.64,h=0.001;
  const f=p=>footLocalOffset(p,stride,sf);
  const velocityBefore=(f(sf)-f(sf-h))/h,velocityAfter=(f(sf+h)-f(sf))/h;
  assert.ok(Math.abs(velocityBefore-velocityAfter)<0.5,"velocity jump: "+velocityBefore+" vs "+velocityAfter);
  const acceleration=p=>(f(p+h)-2*f(p)+f(p-h))/(h*h);
  assert.ok(Math.abs(acceleration(sf))<80,"acceleration spike at toe-off: "+acceleration(sf));
  const cycleEnd=(f(1-h)-2*f(1)+f(h))/(h*h);
  assert.ok(Math.abs(cycleEnd)<80,"acceleration spike at cycle wrap: "+cycleEnd);
});

test("calm gait profile stays inside bounded motion envelopes",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const report=summarizeScene(scene,mode),m=report.motionEnvelopeDiagnostics;
    assert.ok(m.cadenceStepsPerMinute>=90&&m.cadenceStepsPerMinute<=102);
    assert.ok(m.swingLiftPx<=10&&m.freeArmSwingAmplitudePx<=18);
    assert.ok(m.torsoSwayPeakDegrees<=3&&m.basketTiltPeakDegrees<=1);
    assert.ok(report.torsoAngleRangeDegrees<6);
    assert.ok(report.headAngleRangeDegrees<3.5);
  }
});
