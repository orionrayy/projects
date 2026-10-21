import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { buildActivityManifest } from "../scripts/render-activity-previews.mjs";

const sourceScene = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));
const scene = { ...sourceScene, fps: 24, duration_frames: 72 };

test("activity manifest reports the C2 curve contract and jerk cross-checks for every clip", () => {
  const manifest = buildActivityManifest(scene);
  assert.equal(manifest.actionCurveModel, "quintic-hermite-c2-zero-knot-acceleration");
  assert.equal(manifest.activityCount, 6);
  const reach = manifest.activities.find(activity => activity.id === "reach");
  assert.ok(reach.maxPoseStepByPointPx.nearWrist < 10.5,
    "reach wrist peak step should retain smoothing margin below the 11.5 px regression ceiling: " +
    reach.maxPoseStepByPointPx.nearWrist);
  for (const activity of manifest.activities) {
    assert.ok(activity.maxJointJerkPxPerFrame3 >= 0 && Number.isFinite(activity.maxJointJerkPxPerFrame3),
      activity.id + " must report finite peak joint jerk");
    assert.ok(activity.maxJointJerkByPointPxPerFrame3 && activity.maxJointJerkFrameByPoint,
      activity.id + " must report joint-wise jerk and the frame where it peaks");
    for (const name of ["pelvis","chest","head","nearElbow","farElbow","nearWrist","farWrist","leftKnee","rightKnee"]) {
      assert.ok(Number.isFinite(activity.maxJointJerkByPointPxPerFrame3[name]),
        activity.id + " has invalid jerk for " + name);
      assert.ok(Number.isInteger(activity.maxJointJerkFrameByPoint[name]),
        activity.id + " has no frame cross-reference for " + name);
    }
    assert.equal(activity.humanVisualAcceptance, "pending",
      "geometric telemetry must not auto-approve artistic quality");
  }
});
