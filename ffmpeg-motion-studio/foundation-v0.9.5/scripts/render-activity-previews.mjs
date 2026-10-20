import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ACTIVITY_NAMES, ACTIVITY_LABELS, evaluateActivity } from "../src/activity-motion.mjs";
import { renderSvgFrame } from "./render-preview.mjs";

const sourceScene = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

export function buildActivityManifest(scene) {
  const activities = [];
  for (const activity of ACTIVITY_NAMES) {
    let maxBoneErrorPx = 0, maxAnkleClampErrorPx = 0, maxArmClampErrorPx = 0, maxKneeStepPx = 0, maxStanceFootDriftPx = 0;
    let maxPelvisDropPx = 0, maxHeadTurnRadians = 0, maxTorsoLeanRadians = 0, maxReachDisplacementPx = 0;
    let maxPickupItemStepPx = 0, maxPickupItemContactErrorPx = 0, maxReachTargetContactErrorPx = 0;
    let initialSeatContactErrorPx = null, finalSeatContactErrorPx = null, reachTargetContactedAtPeak = false, previous = null;
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateActivity(scene, frame, activity, "free");
      maxBoneErrorPx = Math.max(maxBoneErrorPx, pose.diagnostics.boneLengthErrorPx);
      maxAnkleClampErrorPx = Math.max(maxAnkleClampErrorPx, pose.diagnostics.ankleClampErrorPx);
      maxArmClampErrorPx = Math.max(maxArmClampErrorPx, pose.diagnostics.armClampErrorPx);
      maxPelvisDropPx = Math.max(maxPelvisDropPx, pose.activityState.pelvisDropPx);
      maxHeadTurnRadians = Math.max(maxHeadTurnRadians, Math.abs(pose.activityState.headTurnRadians));
      maxTorsoLeanRadians = Math.max(maxTorsoLeanRadians, Math.abs(pose.activityState.torsoLeanRadians));
      maxReachDisplacementPx = Math.max(maxReachDisplacementPx, pose.activityState.reachDisplacementPx);
      if (frame === 0) initialSeatContactErrorPx = pose.diagnostics.seatContactErrorPx;
      if (frame === scene.duration_frames - 1) finalSeatContactErrorPx = pose.diagnostics.seatContactErrorPx;
      if (pose.activityState.pickupItem?.held) {
        maxPickupItemContactErrorPx = Math.max(maxPickupItemContactErrorPx,
          pose.diagnostics.pickupItemContactErrorPx || 0);
      }
      if (pose.activityState.reachTarget?.active) {
        reachTargetContactedAtPeak = true;
        maxReachTargetContactErrorPx = Math.max(maxReachTargetContactErrorPx,
          pose.diagnostics.reachTargetContactErrorPx ?? Infinity);
      }
      if (previous) {
        const oldItem = previous.activityState.pickupItem, newItem = pose.activityState.pickupItem;
        if (oldItem && newItem) {
          maxPickupItemStepPx = Math.max(maxPickupItemStepPx, Math.hypot(newItem.x-oldItem.x, newItem.y-oldItem.y));
        }
        for (const side of ["left", "right"]) {
          const a = previous[side + "Leg"].knee, b = pose[side + "Leg"].knee;
          maxKneeStepPx = Math.max(maxKneeStepPx, Math.hypot(b.x-a.x,b.y-a.y));
          const oldFoot = previous[side + "Foot"], newFoot = pose[side + "Foot"];
          maxStanceFootDriftPx = Math.max(maxStanceFootDriftPx, Math.hypot(newFoot.x-oldFoot.x,newFoot.y-oldFoot.y));
        }
      }
      previous = pose;
    }
    activities.push({
      id: activity, label: ACTIVITY_LABELS[activity], fps: scene.fps,
      frameCount: scene.duration_frames, durationSeconds: scene.duration_frames / scene.fps,
      maxBoneErrorPx, maxAnkleClampErrorPx, maxArmClampErrorPx, maxKneeStepPx, maxStanceFootDriftPx,
      maxPelvisDropPx, maxHeadTurnRadians, maxTorsoLeanRadians, maxReachDisplacementPx,
      pickupObjectRendered: activity === "pick-up" && renderSvgFrame(scene, scene.duration_frames - 1, "free", activity).includes('data-prop="pickup-item"'),
      pickupObjectHeldAtEnd: activity === "pick-up" ? Boolean(previous?.activityState.pickupItem?.held) : null,
      maxPickupItemStepPx: activity === "pick-up" ? maxPickupItemStepPx : null,
      maxPickupItemContactErrorPx: activity === "pick-up" ? maxPickupItemContactErrorPx : null,
      chairRendered: activity === "sit-to-stand" && renderSvgFrame(scene, 0, "free", activity).includes('data-environment="chair"'),
      initialSeatContactErrorPx: activity === "sit-to-stand" ? initialSeatContactErrorPx : null,
      finalSeatContactErrorPx: activity === "sit-to-stand" ? finalSeatContactErrorPx : null,
      reachTargetRendered: activity === "reach" && renderSvgFrame(scene, Math.floor(scene.duration_frames / 2), "free", activity).includes('data-environment="reach-target"'),
      reachTargetContactedAtPeak: activity === "reach" ? reachTargetContactedAtPeak : null,
      maxReachTargetContactErrorPx: activity === "reach" ? maxReachTargetContactErrorPx : null,
      humanVisualAcceptance: "pending"
    });
  }
  return {
    schemaVersion: "1.3.0", sceneId: "motion-studio-activity-suite-v0.9.5",
    renderer: "procedural SVG + FFmpeg H.264", canvas: scene.canvas, fps: scene.fps,
    activityCount: activities.length, activities,
    limitation: "2D side-profile action proof; turn-in-place is torso/head counter-rotation, not full 3D yaw",
    audioIncluded: false, browserFfmpegParity: "not_verified", humanFullSpeedAcceptance: "pending"
  };
}
export function renderActivityPreviews(outputDirectory) {
  const out = path.resolve(outputDirectory || ".working/activities");
  fs.mkdirSync(out, { recursive: true });
  const scene = { ...sourceScene, fps: 24, duration_frames: 72, scene_version: "0.9.5" };
  const renderJobs = [];
  for (const activity of ACTIVITY_NAMES) {
    const dir = path.join(out, activity);
    fs.mkdirSync(dir, { recursive: true });
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const svg = renderSvgFrame(scene, frame, "free", activity);
      const file = path.join(dir, "frame-" + String(frame).padStart(4, "0") + ".svg");
      fs.writeFileSync(file, svg, "utf8");
    }
    renderJobs.push({ activity, frameCount: scene.duration_frames,
      relativeDirectory: path.relative(out, dir).split(path.sep).join("/") });
  }
  const manifest = buildActivityManifest(scene);
  manifest.outputs = renderJobs;
  fs.writeFileSync(path.join(out, "activity-manifest.json"), JSON.stringify(manifest, null, 2) + "\n", "utf8");
  return { outputDirectory: out, ...manifest };
}
if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  process.stdout.write(JSON.stringify(renderActivityPreviews(process.argv[2] || ".working/activities"), null, 2) + "\n");
}
