import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ACTIVITY_NAMES, ACTIVITY_LABELS, evaluateActivity } from "../src/activity-motion.mjs";
import { renderSvgFrame } from "./render-preview.mjs";

const sourceScene = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

export function buildActivityManifest(scene) {
  const activities = [];
  for (const activity of ACTIVITY_NAMES) {
    let maxBoneErrorPx = 0, maxAnkleClampErrorPx = 0, maxArmClampErrorPx = 0, maxKneeStepPx = 0, maxKneeStepFrame = 0, maxStanceFootDriftPx = 0;
    let maxPelvisDropPx = 0, maxHeadTurnRadians = 0, maxTorsoLeanRadians = 0, maxReachDisplacementPx = 0;
    let maxPickupItemStepPx = 0, maxPickupItemStepFrame = 0, maxPickupItemAccelerationPxPerFrame2 = 0;
    let maxPickupItemContactErrorPx = 0, maxReachTargetContactErrorPx = 0;
    let maxNearArmTargetReachPx = 0, maxFarArmTargetReachPx = 0;
    let pickupAnticipationFrame = null, pickupDescentFrame = null, pickupReachFrame = null;
    let pickupGripFrame = null, pickupLiftFrame = null;
    const trackedPointNames = ["pelvis","chest","head","nearElbow","farElbow","nearWrist","farWrist","leftKnee","rightKnee"];
    const maxPoseStepByPointPx = Object.fromEntries(trackedPointNames.map(name => [name, 0]));
    const maxPoseStepFrameByPoint = Object.fromEntries(trackedPointNames.map(name => [name, 0]));
    const maxJointAccelerationByPointPxPerFrame2 = Object.fromEntries(trackedPointNames.map(name => [name, 0]));
    const maxJointAccelerationFrameByPoint = Object.fromEntries(trackedPointNames.map(name => [name, 0]));
    let maxJointAccelerationPxPerFrame2 = 0;
    let initialSeatContactErrorPx = null, finalSeatContactErrorPx = null, reachTargetContactedAtPeak = false;
    let pickupGripContactFrames = 0, pickupGripContactViolation = false, maxReachWeight = 0;
    let finalPickupItemChestDistancePx = null, previousPrevious = null, previous = null;
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateActivity(scene, frame, activity, "free");
      maxBoneErrorPx = Math.max(maxBoneErrorPx, pose.diagnostics.boneLengthErrorPx);
      maxAnkleClampErrorPx = Math.max(maxAnkleClampErrorPx, pose.diagnostics.ankleClampErrorPx);
      maxArmClampErrorPx = Math.max(maxArmClampErrorPx, pose.diagnostics.armClampErrorPx);
      maxNearArmTargetReachPx = Math.max(maxNearArmTargetReachPx,
        Math.hypot(pose.nearArm.target.x - pose.nearArm.shoulder.x, pose.nearArm.target.y - pose.nearArm.shoulder.y));
      maxFarArmTargetReachPx = Math.max(maxFarArmTargetReachPx,
        Math.hypot(pose.farArm.target.x - pose.farArm.shoulder.x, pose.farArm.target.y - pose.farArm.shoulder.y));
      maxPelvisDropPx = Math.max(maxPelvisDropPx, pose.activityState.pelvisDropPx);
      maxHeadTurnRadians = Math.max(maxHeadTurnRadians, Math.abs(pose.activityState.headTurnRadians));
      maxTorsoLeanRadians = Math.max(maxTorsoLeanRadians, Math.abs(pose.activityState.torsoLeanRadians));
      maxReachDisplacementPx = Math.max(maxReachDisplacementPx, pose.activityState.reachDisplacementPx);
      maxReachWeight = Math.max(maxReachWeight, pose.activityState.reachWeight ?? 0);
      if (frame === 0) initialSeatContactErrorPx = pose.diagnostics.seatContactErrorPx;
      if (frame === scene.duration_frames - 1) {
        finalSeatContactErrorPx = pose.diagnostics.seatContactErrorPx;
        finalPickupItemChestDistancePx = pose.diagnostics.pickupItemChestDistancePx;
      }
      if (activity === "pick-up") {
        if (pickupAnticipationFrame === null && pose.activityState.pickupAnticipationWeight > 0.8) pickupAnticipationFrame = frame;
        if (pickupDescentFrame === null && pose.activityState.pelvisDropPx > 5) pickupDescentFrame = frame;
        if (pickupReachFrame === null && pose.activityState.pickupReachWeight > 0.8) pickupReachFrame = frame;
        if (pickupGripFrame === null && pose.activityState.pickupItem?.held) pickupGripFrame = frame;
        if (pickupLiftFrame === null && pose.activityState.pickupLiftWeight > 0.1) pickupLiftFrame = frame;
      }
      // Count real attachment frames only; a nearly closed hand before attachment
      // is not evidence of object-hand contact.
      if (pose.activityState.pickupItem?.held && pose.activityState.pickupItem?.gripWeight >= 0.95) {
        const contactError = pose.diagnostics.pickupItemContactErrorPx ?? Infinity;
        pickupGripContactFrames++;
        maxPickupItemContactErrorPx = Math.max(maxPickupItemContactErrorPx, contactError);
        if (contactError >= 2) pickupGripContactViolation = true;
      }
      if (pose.activityState.reachTarget?.active) {
        reachTargetContactedAtPeak = true;
        maxReachTargetContactErrorPx = Math.max(maxReachTargetContactErrorPx,
          pose.diagnostics.reachTargetContactErrorPx ?? Infinity);
      }
      if (previous) {
        const oldItem = previous.activityState.pickupItem, newItem = pose.activityState.pickupItem;
        if (oldItem && newItem) {
          const itemStep = Math.hypot(newItem.x-oldItem.x,newItem.y-oldItem.y);
          if (itemStep > maxPickupItemStepPx) { maxPickupItemStepPx = itemStep; maxPickupItemStepFrame = frame; }
          const olderItem = previousPrevious?.activityState.pickupItem;
          if (olderItem) {
            const itemAccel = Math.hypot(newItem.x - 2*oldItem.x + olderItem.x, newItem.y - 2*oldItem.y + olderItem.y);
            maxPickupItemAccelerationPxPerFrame2 = Math.max(maxPickupItemAccelerationPxPerFrame2, itemAccel);
          }
        }
        const points = {
          pelvis: pose.pelvis, chest: pose.chest, head: pose.head,
          nearElbow: pose.nearArm.elbow, farElbow: pose.farArm.elbow,
          nearWrist: pose.nearArm.wrist, farWrist: pose.farArm.wrist,
          leftKnee: pose.leftLeg.knee, rightKnee: pose.rightLeg.knee
        };
        const previousPoints = {
          pelvis: previous.pelvis, chest: previous.chest, head: previous.head,
          nearElbow: previous.nearArm.elbow, farElbow: previous.farArm.elbow,
          nearWrist: previous.nearArm.wrist, farWrist: previous.farArm.wrist,
          leftKnee: previous.leftLeg.knee, rightKnee: previous.rightLeg.knee
        };
        const olderPoints = previousPrevious ? {
          pelvis: previousPrevious.pelvis, chest: previousPrevious.chest, head: previousPrevious.head,
          nearElbow: previousPrevious.nearArm.elbow, farElbow: previousPrevious.farArm.elbow,
          nearWrist: previousPrevious.nearArm.wrist, farWrist: previousPrevious.farArm.wrist,
          leftKnee: previousPrevious.leftLeg.knee, rightKnee: previousPrevious.rightLeg.knee
        } : null;
        for (const name of trackedPointNames) {
          const a = previousPoints[name], b = points[name];
          const step = Math.hypot(b.x-a.x,b.y-a.y);
          if (step > maxPoseStepByPointPx[name]) {
            maxPoseStepByPointPx[name] = step;
            maxPoseStepFrameByPoint[name] = frame;
          }
          if ((name === "leftKnee" || name === "rightKnee") && step > maxKneeStepPx) {
            maxKneeStepPx = step; maxKneeStepFrame = frame;
          }
          if (olderPoints) {
            const p2 = olderPoints[name];
            const acceleration = Math.hypot(b.x - 2*a.x + p2.x, b.y - 2*a.y + p2.y);
            if (acceleration > maxJointAccelerationByPointPxPerFrame2[name]) {
              maxJointAccelerationByPointPxPerFrame2[name] = acceleration;
              maxJointAccelerationFrameByPoint[name] = frame;
            }
            maxJointAccelerationPxPerFrame2 = Math.max(maxJointAccelerationByPointPxPerFrame2[name], maxJointAccelerationPxPerFrame2);
          }
        }
        for (const side of ["left", "right"]) {
          const oldFoot = previous[side + "Foot"], newFoot = pose[side + "Foot"];
          maxStanceFootDriftPx = Math.max(maxStanceFootDriftPx, Math.hypot(newFoot.x-oldFoot.x,newFoot.y-oldFoot.y));
        }
      }
      previousPrevious = previous;
      previous = pose;
    }
    activities.push({
      id: activity, label: ACTIVITY_LABELS[activity], fps: scene.fps,
      frameCount: scene.duration_frames, durationSeconds: scene.duration_frames / scene.fps,
      cameraFraming: "close-action-1.50x",
      maxBoneErrorPx, maxAnkleClampErrorPx, maxArmClampErrorPx, maxKneeStepPx, maxKneeStepFrame, maxStanceFootDriftPx,
      maxPoseStepByPointPx, maxPoseStepFrameByPoint,
      maxJointAccelerationByPointPxPerFrame2, maxJointAccelerationFrameByPoint, maxJointAccelerationPxPerFrame2,
      maxNearArmTargetReachPx, maxFarArmTargetReachPx,
      maxPickupItemAccelerationPxPerFrame2, maxPickupItemStepFrame,
      temporalMetricsFinite: [...Object.values(maxPoseStepByPointPx), ...Object.values(maxJointAccelerationByPointPxPerFrame2),
        maxJointAccelerationPxPerFrame2, maxPickupItemAccelerationPxPerFrame2].every(Number.isFinite),
      maxPelvisDropPx, maxHeadTurnRadians, maxTorsoLeanRadians, maxReachDisplacementPx,
      pickupObjectRendered: activity === "pick-up" && renderSvgFrame(scene, scene.duration_frames - 1, "free", activity).includes('data-prop="pickup-item"'),
      pickupObjectHeldAtEnd: activity === "pick-up" ? Boolean(previous?.activityState.pickupItem?.held) : null,
      maxPickupItemStepPx: activity === "pick-up" ? maxPickupItemStepPx : null,
      maxPickupItemContactErrorPx: activity === "pick-up" ? maxPickupItemContactErrorPx : null,
      pickupObjectContactedWhileGripping: activity === "pick-up"
        ? pickupGripContactFrames >= 20 && !pickupGripContactViolation : null,
      pickupGripContactFrames: activity === "pick-up" ? pickupGripContactFrames : null,
      pickupPhaseFrames: activity === "pick-up" ? {
        anticipation: pickupAnticipationFrame, descent: pickupDescentFrame, reach: pickupReachFrame,
        grip: pickupGripFrame, lift: pickupLiftFrame
      } : null,
      finalPickupItemChestDistancePx: activity === "pick-up" ? finalPickupItemChestDistancePx : null,
      maxReachWeight: activity === "reach" ? maxReachWeight : null,
      reachReturnsToRest: activity === "reach" ? previous.activityState.reachWeight < 0.1 : null,
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
    schemaVersion: "1.5.0", sceneId: "motion-studio-activity-suite-v0.9.5",
    renderer: "procedural SVG + FFmpeg H.264", canvas: scene.canvas, fps: scene.fps,
    actionCurveModel: "shape-preserving-cubic-keyframes",
    cameraFraming: { activityClips: "close-action-1.50x", floorAnchor: "screen-space horizon; planted feet remain grounded" },
    evaluationPolicy: "geometry, phase timing, semantic contact and all-frame review are separate acceptance gates",
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
