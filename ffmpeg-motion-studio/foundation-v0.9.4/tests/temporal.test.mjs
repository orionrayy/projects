import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {summarizeScene} from "../scripts/render-preview.mjs";
import {evaluateLocomotion} from "../src/locomotion.mjs";
import {footLocalOffset, swingLiftPulse} from "../src/locomotion.mjs";

const carry = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"));
const free = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

test("frame-step and acceleration metrics are finite and bounded", () => {
  for (const [scene, mode] of [[carry,"carry"],[free,"free"]]) {
    const report = summarizeScene(scene,mode);
    const t = report.temporalDiagnostics;
    assert.equal(t.allTemporalMetricsFinite,true);
    assert.ok(t.maxHeadStepPx < 6.0, "head step spikes: " + t.maxHeadStepPx);
    assert.ok(t.maxChestStepPx < 6.5, "chest motion is too active: " + t.maxChestStepPx);
    assert.ok(t.maxNearElbowStepPx < 8.0, "near elbow step spikes: " + t.maxNearElbowStepPx);
    assert.ok(t.maxFarElbowStepPx < 8.0, "far elbow step spikes: " + t.maxFarElbowStepPx);
    assert.ok(t.maxNearWristStepPx < 11.5, "near wrist step spikes: " + t.maxNearWristStepPx);
    assert.ok(t.maxFarWristStepPx < 11.5, "far wrist step spikes: " + t.maxFarWristStepPx);
    assert.ok(t.maxKneeStepPx < 13.0, "knee step spikes: " + t.maxKneeStepPx);
    assert.ok(t.maxFootStepPx < 16.0, "foot step spikes: " + t.maxFootStepPx);
    const accelerationLimit = Math.max(8, report.motionEnvelopeDiagnostics.strideLengthPx * 0.12);
    assert.ok(t.maxJointAccelerationPxPerFrame2 < accelerationLimit, "joint acceleration spikes (scaled stride limit " + accelerationLimit.toFixed(2) + "): " + JSON.stringify(t));
    assert.ok(t.stanceFootSamplePairs > 100, "insufficient stance samples to support drift metric");
    assert.ok(t.stanceTransitions > 10, "contact-state transitions were not sampled");
  }
});


test("swing lift has C2-smooth contact and apex boundaries", () => {
  assert.equal(swingLiftPulse(0), 0);
  assert.equal(swingLiftPulse(0.5), 1);
  assert.equal(swingLiftPulse(1), 0);
  for (let i = 0; i <= 100; i++) {
    const u = i / 100;
    assert.ok(swingLiftPulse(u) >= 0 && swingLiftPulse(u) <= 1);
    assert.ok(Math.abs(swingLiftPulse(u) - swingLiftPulse(1 - u)) < 1e-12);
    if (i < 100) {
      const next = (i + 1) / 100;
      if (u < 0.5) assert.ok(swingLiftPulse(next) >= swingLiftPulse(u) - 1e-12);
      if (u >= 0.5) assert.ok(swingLiftPulse(next) <= swingLiftPulse(u) + 1e-12);
    }
  }
  const h = 1e-3;
  for (const boundary of [0, 0.5, 1]) {
    const first = (swingLiftPulse(boundary + h) - swingLiftPulse(boundary - h)) / (2 * h);
    const second = (swingLiftPulse(boundary + h) - 2 * swingLiftPulse(boundary) + swingLiftPulse(boundary - h)) / (h * h);
    assert.ok(Math.abs(first) < 0.01, "nonzero swing-lift velocity at " + boundary + ": " + first);
    assert.ok(Math.abs(second) < 1, "nonzero swing-lift acceleration at " + boundary + ": " + second);
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

test("adaptive gait profile stays inside bounded motion envelopes",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const report=summarizeScene(scene,mode),m=report.motionEnvelopeDiagnostics;
    assert.ok(m.cadenceStepsPerMinute>=90&&m.cadenceStepsPerMinute<=102);
    assert.ok(m.swingLiftPx<=18&&m.freeArmSwingAmplitudePx<=24);
    assert.ok(m.strideLengthPx>=92,"effective stride must remain above the v0.9.3 baseline: "+m.strideLengthPx);
    assert.ok(m.torsoSwayPeakDegrees<=4&&m.basketTiltPeakDegrees<=1.5);
    assert.ok(report.torsoAngleRangeDegrees<9);
    assert.ok(report.headAngleRangeDegrees<6.5);
  }
});


test("ankle reach diagnostics identify the exact frame if leg geometry becomes unreachable", () => {
  for (const [scene, mode] of [[carry,"carry"],[free,"free"]]) {
    let worst = { error: -1 };
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateLocomotion(scene, frame, mode);
      for (const side of ["left","right"]) {
        const leg = side === "left" ? pose.leftLeg : pose.rightLeg;
        if (leg.endpointClampErrorPx > worst.error) {
          worst = { error: leg.endpointClampErrorPx, frame, side, hip: leg.hip,
            target: side === "left" ? pose.leftFoot : pose.rightFoot, solvedAnkle: leg.end,
            requestedReachPx: leg.requestedReachPx, solvedReachPx: leg.solvedReachPx };
        }
      }
    }
    assert.ok(worst.error < 1.5, mode + " ankle reach exceeds tolerance: " + JSON.stringify(worst));
  }
});
