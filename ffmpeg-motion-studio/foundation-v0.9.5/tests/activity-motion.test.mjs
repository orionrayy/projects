import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { ACTIVITY_NAMES, evaluateActivity } from "../src/activity-motion.mjs";
import { renderSvgFrame } from "../scripts/render-preview.mjs";
import { buildActivityManifest } from "../scripts/render-activity-previews.mjs";

const source = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));
const scene = { ...source, fps: 24, duration_frames: 72 };

test("activity catalog includes six deterministic non-walk motion families", () => {
  assert.deepEqual([...ACTIVITY_NAMES], ["stand", "look-around", "reach", "pick-up", "sit-to-stand", "turn-in-place"]);
});

test("all activity clips preserve grounded feet, finite poses and solved bone lengths", () => {
  for (const activity of ACTIVITY_NAMES) {
    let maxBoneError = 0, maxAnkleClamp = 0, maxArmClamp = 0, maxKneeStep = 0, maxFootDrift = 0;
    let previous = null;
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateActivity(scene, frame, activity, "free");
      assert.ok(Number.isFinite(pose.pelvis.x) && Number.isFinite(pose.pelvis.y), activity + " pelvis is non-finite");
      assert.equal(pose.diagnostics.stance.left, true, activity + " left foot must stay planted");
      assert.equal(pose.diagnostics.stance.right, true, activity + " right foot must stay planted");
      assert.ok(Math.abs(pose.leftFoot.y - scene.background.horizon_y) < 1e-8, activity + " left foot left the floor");
      assert.ok(Math.abs(pose.rightFoot.y - scene.background.horizon_y) < 1e-8, activity + " right foot left the floor");
      maxBoneError = Math.max(maxBoneError, pose.diagnostics.boneLengthErrorPx);
      maxAnkleClamp = Math.max(maxAnkleClamp, pose.diagnostics.ankleClampErrorPx);
      maxArmClamp = Math.max(maxArmClamp, pose.diagnostics.armClampErrorPx);
      if (previous) {
        for (const side of ["left", "right"]) {
          const a = previous[side + "Leg"].knee, b = pose[side + "Leg"].knee;
          maxKneeStep = Math.max(maxKneeStep, Math.hypot(b.x - a.x, b.y - a.y));
          const oldFoot = previous[side + "Foot"], newFoot = pose[side + "Foot"];
          maxFootDrift = Math.max(maxFootDrift, Math.hypot(newFoot.x - oldFoot.x, newFoot.y - oldFoot.y));
        }
      }
      previous = pose;
    }
    assert.ok(maxBoneError < 0.02, activity + " bone error: " + maxBoneError);
    assert.ok(maxAnkleClamp < 1.5, activity + " ankle clamp: " + maxAnkleClamp);
    assert.ok(maxArmClamp < 1.5, activity + " arm clamp: " + maxArmClamp);
    assert.ok(maxKneeStep < 13, activity + " knee step: " + maxKneeStep);
    assert.ok(maxFootDrift < 0.05, activity + " foot drift: " + maxFootDrift);
  }
});

test("each non-walk clip visibly changes its intended control channel", () => {
  const summarize = (activity) => {
    const poses = Array.from({ length: scene.duration_frames }, (_, frame) => evaluateActivity(scene, frame, activity, "free"));
    return {
      poses,
      minDrop: Math.min(...poses.map(p => p.activityState.pelvisDropPx)),
      maxDrop: Math.max(...poses.map(p => p.activityState.pelvisDropPx)),
      minHead: Math.min(...poses.map(p => p.headAngle)),
      maxHead: Math.max(...poses.map(p => p.headAngle)),
      minTorso: Math.min(...poses.map(p => p.torsoAngle)),
      maxTorso: Math.max(...poses.map(p => p.torsoAngle)),
      maxReach: Math.max(...poses.map(p => p.activityState.reachDisplacementPx))
    };
  };
  const look = summarize("look-around");
  assert.ok(look.maxHead - look.minHead > 0.45);
  assert.ok(summarize("reach").maxReach >= 70);
  assert.ok(summarize("pick-up").maxDrop >= 18);
  const sit = summarize("sit-to-stand");
  assert.ok(sit.poses[0].activityState.pelvisDropPx > 20);
  assert.ok(sit.poses.at(-1).activityState.pelvisDropPx < 0.1);
  const turn = summarize("turn-in-place");
  assert.ok(turn.maxTorso - turn.minTorso > 0.22);
});

test("pick-up shows a real object, keeps it on the table before grasp, and ends holding it", () => {
  const first = evaluateActivity(scene, 0, "pick-up", "free");
  const last = evaluateActivity(scene, scene.duration_frames - 1, "pick-up", "free");
  assert.ok(first.activityState.pickupItem, "pickup item metadata missing at start");
  assert.ok(Math.abs(first.activityState.pickupItem.y + first.activityState.pickupItem.height / 2 -
    first.activityState.pickupItem.tableTopY) < 1e-8, "item must begin resting on its table");
  assert.equal(first.activityState.pickupItem.held, false);
  assert.equal(last.activityState.pickupItem.held, true, "the item should remain held at clip end");
  assert.ok(last.diagnostics.pickupItemContactErrorPx < 1e-8, "held item must stay attached to the hand");

  let previous = first.activityState.pickupItem, maxItemStep = 0;
  for (let frame = 1; frame < scene.duration_frames; frame++) {
    const current = evaluateActivity(scene, frame, "pick-up", "free").activityState.pickupItem;
    maxItemStep = Math.max(maxItemStep, Math.hypot(current.x - previous.x, current.y - previous.y));
    previous = current;
  }
  assert.ok(maxItemStep < 15, "pickup prop trajectory has a step spike: " + maxItemStep);
  const svg = renderSvgFrame(scene, scene.duration_frames - 1, "free", "pick-up");
  assert.ok(svg.includes('data-prop="pickup-item"'));
  assert.ok(svg.includes('data-environment="pickup-table"'));
});

test("sit-to-stand includes a stable chair behind the character", () => {
  const pose = evaluateActivity(scene, 0, "sit-to-stand", "free");
  assert.ok(pose.activityState.chair, "chair context missing from sit-to-stand");
  assert.ok(pose.activityState.chair.seatY < pose.activityState.chair.floorY);
  assert.ok(pose.diagnostics.seatContactErrorPx < 1, "initial pose should contact the chair seat");
  const finalPose = evaluateActivity(scene, scene.duration_frames - 1, "sit-to-stand", "free");
  assert.ok(finalPose.activityState.pelvisDropPx < 0.1, "final pose should be standing");
  assert.ok(finalPose.diagnostics.seatContactErrorPx > 20, "final pose must clear the seat");
  const svg = renderSvgFrame(scene, 0, "free", "sit-to-stand");
  assert.ok(svg.includes('data-environment="chair"'));
});

test("activity manifest records semantic props and interaction continuity", () => {
  const manifest = buildActivityManifest(scene);
  assert.equal(manifest.schemaVersion, "1.1.0");
  const pickup = manifest.activities.find(item => item.id === "pick-up");
  const sit = manifest.activities.find(item => item.id === "sit-to-stand");
  assert.equal(pickup.pickupObjectRendered, true);
  assert.equal(pickup.pickupObjectHeldAtEnd, true);
  assert.ok(pickup.maxPickupItemStepPx < 15);
  assert.ok(pickup.maxPickupItemContactErrorPx < 1e-8);
  assert.equal(sit.chairRendered, true);
  assert.ok(sit.initialSeatContactErrorPx < 1);
  assert.ok(sit.finalSeatContactErrorPx > 20);
  assert.equal(manifest.schemaVersion, "1.2.0");
  assert.equal(manifest.humanFullSpeedAcceptance, "pending");
});

test("SVG renderer tags and labels every activity preview", () => {
  for (const activity of ACTIVITY_NAMES) {
    const svg = renderSvgFrame(scene, 36, "free", activity);
    assert.ok(svg.includes('data-activity="' + activity + '"'));
    assert.ok(svg.includes('data-activity-overlay="label"'));
    assert.ok(svg.includes("MOTION STUDIO / v0.9.5"));
  }
  assert.throws(() => renderSvgFrame(scene, 20, "free", "unknown-action"), /Unsupported activity/);
});
