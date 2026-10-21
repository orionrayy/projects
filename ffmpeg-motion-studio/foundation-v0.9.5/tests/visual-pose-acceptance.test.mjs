import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { evaluateActivity } from "../src/activity-motion.mjs";
import { renderSvgFrame } from "../scripts/render-preview.mjs";

const source = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));
const scene = { ...source, fps: 24, duration_frames: 72 };
const dist = (a, b) => Math.hypot(a.x - b.x, a.y - b.y);
const frame = (activity, i) => evaluateActivity(scene, i, activity, "free");

function handAngles(svg) {
  return [...svg.matchAll(/data-hand-angle-degrees="(-?[\d.]+)"/g)].map(m => Number(m[1]));
}

test("neutral profiles separate projected feet and place hands on distinct sides", () => {
  for (const activity of ["stand", "look-around", "turn-in-place"]) {
    const p = frame(activity, 0);
    assert.ok(Math.abs(p.leftFoot.x - p.rightFoot.x) >= 10, activity + ": projected shoes overlap");
    assert.ok(p.nearArm.wrist.x > p.farArm.wrist.x + 15, activity + ": near and far wrists collapsed");
    const svg = renderSvgFrame(scene, 0, "free", activity);
    assert.ok(svg.includes('data-contour-frame="spine-aligned"'), activity + ": torso contour is not spine-aligned");
    assert.ok(svg.includes('data-hand-side="near"') && svg.includes('data-hand-side="far"'));
    const angles = handAngles(svg);
    assert.equal(angles.length, 2);
    for (const angle of angles) {
      assert.ok(angle >= 55 && angle <= 125, activity + ": relaxed hand orientation looks inverted: " + angle);
    }
  }
});

test("standing legs extend and foot depth matches the corresponding hip projection", () => {
  const stand = frame("stand", 0);
  for (const side of ["left", "right"]) {
    const foot = stand[side + "Foot"], hip = stand[side + "Hip"], leg = stand[side + "Leg"];
    assert.ok(Math.abs(foot.x - hip.x) < 1, side + ": foot and hip depth projection diverged");
    assert.ok(leg.jointAngleDegrees > 160, side + ": neutral standing knee is too flexed: " + leg.jointAngleDegrees);
  }
  const seated = frame("sit-to-stand", 0);
  const upright = frame("sit-to-stand", 71);
  assert.ok(upright.leftLeg.jointAngleDegrees > seated.leftLeg.jointAngleDegrees + 40,
    "sit-to-stand must visibly extend the knees from the seated starting pose");
  assert.ok(upright.leftLeg.jointAngleDegrees > 160, "terminal standing pose should approach full extension");
});

test("reach action changes hand semantics from pointing to pressing", () => {
  const approach = renderSvgFrame(scene, 28, "free", "reach");
  const contact = renderSvgFrame(scene, 36, "free", "reach");
  assert.ok(approach.includes('data-hand-pose="point"'), "approach should show a pointing/reaching hand");
  assert.ok(contact.includes('data-hand-pose="press"'), "target contact should show a pressing hand");
  assert.ok(contact.includes('data-button-state="pressed"'));
  assert.ok(contact.includes('data-anatomy="index-finger"'));
  const p = frame("reach", 36);
  assert.equal(p.activityState.reachTarget.active, true);
  assert.ok(p.diagnostics.reachTargetContactErrorPx < 1e-6);
});

test("pickup switches to a grip hand and preserves parcel contact", () => {
  const p = frame("pick-up", 71);
  const svg = renderSvgFrame(scene, 71, "free", "pick-up");
  assert.ok(svg.includes('data-hand-pose="grip"'));
  assert.ok(svg.includes('data-prop="pickup-item"'));
  assert.equal(p.activityState.pickupItem.held, true);
  assert.ok(p.diagnostics.pickupItemContactErrorPx < 2);
});

test("the torso contour follows trunk displacement rather than staying vertical", () => {
  const p = frame("sit-to-stand", 31);
  const svg = renderSvgFrame(scene, 31, "free", "sit-to-stand");
  assert.ok(p.activityState.torsoLeanRadians > 0.28, "forward anticipation should be visible");
  assert.ok(svg.includes('data-contour-frame="spine-aligned"'));
  assert.ok(svg.includes('data-torso-detail="seam"'));
});

test("all six action families expose explicit hand-side and hand-pose metadata", () => {
  for (const activity of ["stand", "look-around", "reach", "pick-up", "sit-to-stand", "turn-in-place"]) {
    const svg = renderSvgFrame(scene, 36, "free", activity);
    assert.equal((svg.match(/data-anatomy="hand"/g) || []).length, 2, activity + ": expected two hands");
    assert.match(svg, /data-hand-side="near"/);
    assert.match(svg, /data-hand-side="far"/);
    assert.match(svg, /data-hand-pose="/);
  }
});
