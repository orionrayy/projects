import { evaluateLocomotion, solveTwoBoneIK } from "./locomotion.mjs";

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const smoothstep = (t) => { const u = clamp(t, 0, 1); return u * u * (3 - 2 * u); };
const TAU = Math.PI * 2;

export const ACTIVITY_NAMES = Object.freeze([
  "stand", "look-around", "reach", "pick-up", "sit-to-stand", "turn-in-place"
]);
export const ACTIVITY_LABELS = Object.freeze({
  "stand": "STAND / BREATH",
  "look-around": "LOOK AROUND",
  "reach": "REACH FORWARD",
  "pick-up": "CROUCH / PICK UP",
  "sit-to-stand": "SIT TO STAND",
  "turn-in-place": "TURN / WEIGHT SHIFT"
});

function pulse(u, rise = 0.2, fall = 0.78) {
  return smoothstep(u / rise) * (1 - smoothstep((u - fall) / (1 - fall)));
}
function rotatePoint(point, pivot, angle) {
  const dx = point.x - pivot.x, dy = point.y - pivot.y;
  const c = Math.cos(angle), s = Math.sin(angle);
  return { ...point, x: pivot.x + dx * c - dy * s, y: pivot.y + dx * s + dy * c };
}
function transformUpper(point, oldPelvis, newPelvis, angle, extraX = 0, extraY = 0) {
  const moved = rotatePoint(point, oldPelvis, angle);
  return { ...point, x: moved.x + (newPelvis.x - oldPelvis.x) + extraX,
    y: moved.y + (newPelvis.y - oldPelvis.y) + extraY };
}
function translatePoint(point, dx, dy) {
  return point && Number.isFinite(point.x) && Number.isFinite(point.y)
    ? { ...point, x: point.x + dx, y: point.y + dy } : point;
}
function limbPack(ik, root, target) {
  return { ...ik, shoulder: { ...root }, elbow: ik.joint, elbowAngleDegrees: ik.jointAngleDegrees,
    wrist: ik.end, target: { ...target } };
}
function solveLeg(hip, foot, scene) {
  const c = scene.character, ankle = { x: foot.x, y: foot.y - 3 };
  const fx = (hip.x + ankle.x) / 2 + (c.knee_forward_bias_px || 14) * (c.stance_knee_forward_ratio ?? 0.42);
  const fy = (hip.y + ankle.y) / 2 - (c.knee_up_bias_px || 12) * (c.stance_knee_up_ratio ?? 0.25);
  const ik = solveTwoBoneIK(hip, ankle, c.upper_leg_px, c.lower_leg_px,
    { x: fx, y: fy, preferForward: true, reachEaseBias: c.knee_reach_ease_bias }, -1);
  return { ...ik, hip: { ...hip }, knee: ik.joint, ankle: ik.end };
}
function solveArm(shoulder, target, scene, counter = -1) {
  const c = scene.character;
  const dx = target.x - shoulder.x, dy = target.y - shoulder.y;
  const dist = Math.hypot(dx, dy);
  const mid = { x: (shoulder.x + target.x) / 2, y: (shoulder.y + target.y) / 2 };
  const pole = { x: mid.x + counter * Math.min(15, Math.max(6, dist * 0.12)), y: mid.y + 12 };
  const ik = solveTwoBoneIK(shoulder, target, c.upper_arm_px, c.forearm_px, pole, -1);
  return limbPack(ik, shoulder, target);
}
function fixedPoseScene(scene, armMode) {
  return {
    ...scene,
    motion: {
      ...scene.motion, cycle_seconds: 1e9, stride_length_px: 0, screen_stride_scale: 0,
      start_ramp_seconds: 0, stop_ramp_seconds: 0, pelvis_bob_px: 0, pelvis_bob_asymmetry_px: 0,
      pelvis_lateral_shift_px: 0, torso_forward_lean_radians: 0, torso_sway_radians: 0,
      secondary_torso_sway_radians: 0, cycle_torso_sway_variation_radians: 0, cycle_torso_shift_variation_px: 0,
      torso_shift_px: 0, head_follow_x_px: 0, head_follow_radians: 0, head_bob_radians: 0,
      contact_response_width_cycles: 0, contact_compression_px: 0, contact_torso_reaction_radians: 0,
      contact_head_counter_radians: 0, contact_chest_shift_px: 0, contact_lateral_shift_px: 0,
      contact_head_drop_px: 0, contact_basket_response_px: 0, contact_basket_tilt_radians: 0,
      contact_arm_reaction_px: 0, cycle_lift_variation_fraction: 0, cycle_arm_variation_fraction: 0,
      arm_lag_cycles: 0, phase_variation_cycles: 0, free_arm_swing_px: 0, free_arm_vertical_swing_px: 0,
      free_arm_drop_px: 68, basket_vertical_response_px: 0, basket_tilt_radians: 0, arm_mode: armMode
    }
  };
}

/**
 * Deterministic procedural action overlays for the current 2D side-profile rig.
 * "turn-in-place" intentionally means torso/head counter-rotation and weight shift;
 * a true 3D yaw/orientation flip requires a 3D or multi-view character rig.
 */
export function evaluateActivity(scene, frameIndex, activity, armMode = "free") {
  if (!ACTIVITY_NAMES.includes(activity)) throw new RangeError("Unsupported activity: " + activity);
  if (armMode !== "carry" && armMode !== "free") throw new RangeError("Unsupported arm mode.");
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= scene.duration_frames) {
    throw new RangeError("Frame is outside activity timeline.");
  }
  const staticScene = fixedPoseScene(scene, armMode);
  const base = evaluateLocomotion(staticScene, frameIndex, armMode);
  const duration = Math.max(1, scene.duration_frames - 1);
  const u = frameIndex / duration;
  const actionPulse = pulse(u, 0.2, 0.78);
  const turnPulse = pulse(u, 0.18, 0.72);
  // Pick-up is a short reach -> grasp -> lift sequence. Keep the object attached
  // through the end of the clip rather than returning it to its starting point.
  const pickupReach = smoothstep(u / 0.23) * (1 - smoothstep((u - 0.24) / 0.27));
  const pickupGrip = smoothstep((u - 0.24) / 0.18);
  const pickupLift = smoothstep((u - 0.38) / 0.25);
  let drop = 0, forwardShift = 0, lean = 0, headTurn = 0, headShift = 0, reachWeight = 0, breath = 0;
  if (activity === "stand") breath = 0.9 * Math.sin(TAU * u);
  if (activity === "look-around") {
    headTurn = 0.32 * Math.sin(TAU * u);
    headShift = 1.8 * Math.sin(TAU * u);
    lean = 0.025 * Math.sin(TAU * u + 0.4);
  }
  if (activity === "reach") {
    reachWeight = actionPulse;
    lean = 0.055 * reachWeight;
    forwardShift = 2 * reachWeight;
  }
  if (activity === "pick-up") {
    drop = 28 * pickupReach;
    forwardShift = 7 * pickupReach;
    lean = 0.40 * pickupReach;
    reachWeight = pickupReach;
  }
  if (activity === "sit-to-stand") {
    drop = 25 * (1 - smoothstep(u));
    forwardShift = 7 * (1 - smoothstep(u));
    lean = 0.24 * (1 - smoothstep(u));
  }
  if (activity === "turn-in-place") {
    lean = 0.24 * turnPulse;
    headTurn = -0.23 * turnPulse;
    forwardShift = 3.5 * turnPulse;
  }

  const oldPelvis = { ...base.pelvis };
  const newPelvis = { x: oldPelvis.x + forwardShift, y: oldPelvis.y + drop - breath };
  const transform = (pt, factor = 1, ex = 0, ey = 0) =>
    transformUpper(pt, oldPelvis, newPelvis, lean * factor, ex, ey);
  const pose = { ...base,
    activityName: activity, activityProgress: u,
    activityState: { pelvisDropPx: drop, torsoLeanRadians: lean, headTurnRadians: headTurn,
      reachWeight, reachDisplacementPx: 76 * reachWeight, breathingOffsetPx: breath,
      pickupReachWeight: activity === "pick-up" ? pickupReach : 0,
      pickupGripWeight: activity === "pick-up" ? pickupGrip : 0,
      pickupLiftWeight: activity === "pick-up" ? pickupLift : 0,
      pickupItem: null, chair: null, reachTarget: null },
    pelvis: newPelvis, rootX: newPelvis.x, torsoAngle: lean,
    chestLocal: transform(base.chestLocal),
    chest: transform(base.chest),
    neck: transform(base.neck, 0.72),
    headLocal: transform(base.headLocal, 0.42, headShift, 0),
    head: transform(base.head, 0.42, headShift, 0),
    headAngle: base.headAngle + headTurn - lean * 0.18,
    shoulders: { near: transform(base.shoulders.near), far: transform(base.shoulders.far) }
  };

  pose.leftFoot = { ...base.leftFoot };
  pose.rightFoot = { ...base.rightFoot };
  pose.leftHip = translatePoint(base.leftHip, forwardShift, drop - breath);
  pose.rightHip = translatePoint(base.rightHip, forwardShift, drop - breath);
  pose.leftLeg = solveLeg(pose.leftHip, pose.leftFoot, staticScene);
  pose.rightLeg = solveLeg(pose.rightHip, pose.rightFoot, staticScene);

  let nearTarget = transform(base.nearArm.wrist);
  let farTarget = transform(base.farArm.wrist);
  if (armMode === "carry") {
    const b = base.basket;
    pose.basket = {
      ...b, x: b.x + forwardShift, y: b.y + drop - breath,
      center: translatePoint(b.center, forwardShift, drop - breath),
      handleLeft: translatePoint(b.handleLeft, forwardShift, drop - breath),
      handleRight: translatePoint(b.handleRight, forwardShift, drop - breath)
    };
    nearTarget = { ...pose.basket.handleRight };
    farTarget = { ...pose.basket.handleLeft };
  } else if (activity === "reach") {
    nearTarget = {
      x: pose.shoulders.near.x + 76 * reachWeight + (base.nearArm.wrist.x - base.shoulders.near.x) * (1 - reachWeight),
      y: pose.shoulders.near.y + 8 * reachWeight + (base.nearArm.wrist.y - base.shoulders.near.y) * (1 - reachWeight)
    };
    farTarget = { x: farTarget.x - 7 * reachWeight, y: farTarget.y - 3 * reachWeight };
  } else if (activity === "pick-up") {
    const reachingTarget = {
      x: pose.shoulders.near.x + 34 * pickupReach + (base.nearArm.wrist.x - base.shoulders.near.x) * (1 - pickupReach),
      y: pose.shoulders.near.y + 84 * pickupReach + (base.nearArm.wrist.y - base.shoulders.near.y) * (1 - pickupReach)
    };
    const holdingTarget = { x: pose.shoulders.near.x + 42, y: pose.shoulders.near.y + 24 };
    nearTarget = {
      x: reachingTarget.x + (holdingTarget.x - reachingTarget.x) * pickupLift,
      y: reachingTarget.y + (holdingTarget.y - reachingTarget.y) * pickupLift
    };
    // The far arm acts as a small counterbalance while the near hand grasps/lifts.
    farTarget = { x: farTarget.x - 6 * pickupReach + 2 * pickupLift,
      y: farTarget.y - 12 * pickupReach - 4 * pickupLift };
  } else if (activity === "sit-to-stand") {
    const counter = 1 - smoothstep(u);
    nearTarget = { x: nearTarget.x - 8 * counter, y: nearTarget.y - 5 * counter };
    farTarget = { x: farTarget.x - 8 * counter, y: farTarget.y - 5 * counter };
  } else if (activity === "turn-in-place") {
    nearTarget = { x: nearTarget.x + 5 * turnPulse, y: nearTarget.y - 2 * turnPulse };
    farTarget = { x: farTarget.x - 4 * turnPulse, y: farTarget.y - 2 * turnPulse };
  }

  pose.nearArm = solveArm(pose.shoulders.near, nearTarget, staticScene, -1);
  pose.farArm = solveArm(pose.shoulders.far, farTarget, staticScene, 1);

  if (activity === "pick-up") {
    const tableTopY = scene.background.horizon_y - 144;
    const origin = { x: base.shoulders.near.x + 50, y: tableTopY - 11 };
    const held = { x: pose.nearArm.wrist.x + 18, y: pose.nearArm.wrist.y };
    pose.activityState.pickupItem = {
      x: origin.x + (held.x - origin.x) * pickupGrip,
      y: origin.y + (held.y - origin.y) * pickupGrip,
      width: 30, height: 22, tableX: origin.x, tableTopY,
      gripWeight: pickupGrip, held: pickupGrip >= 0.999999
    };
  }
  if (activity === "sit-to-stand") {
    pose.activityState.chair = {
      x: base.pelvis.x - 8,
      seatY: scene.background.horizon_y - 145,
      floorY: scene.background.horizon_y
    };
  }
  if (activity === "reach") {
    pose.activityState.reachTarget = {
      x: pose.shoulders.near.x + 76,
      y: pose.shoulders.near.y + 8,
      radius: 10,
      active: reachWeight >= 0.999999999
    };
  }
  pose.basketCenter = pose.basket?.center || translatePoint(base.basketCenter, forwardShift, drop - breath);
  const boneErrors = [
    pose.leftLeg.upperErrorPx, pose.leftLeg.lowerErrorPx, pose.rightLeg.upperErrorPx, pose.rightLeg.lowerErrorPx,
    pose.nearArm.upperErrorPx, pose.nearArm.lowerErrorPx, pose.farArm.upperErrorPx, pose.farArm.lowerErrorPx
  ];
  pose.diagnostics = {
    ...base.diagnostics,
    boneLengthErrorPx: Math.max(...boneErrors),
    ankleClampErrorPx: Math.max(pose.leftLeg.endpointClampErrorPx, pose.rightLeg.endpointClampErrorPx),
    armClampErrorPx: Math.max(pose.nearArm.endpointClampErrorPx, pose.farArm.endpointClampErrorPx),
    basketContactErrorPx: armMode === "carry" ? Math.max(
      Math.hypot(pose.nearArm.wrist.x - pose.basket.handleRight.x, pose.nearArm.wrist.y - pose.basket.handleRight.y),
      Math.hypot(pose.farArm.wrist.x - pose.basket.handleLeft.x, pose.farArm.wrist.y - pose.basket.handleLeft.y)
    ) : 0,
    pickupItemContactErrorPx: pose.activityState.pickupItem?.held
      ? Math.hypot(pose.activityState.pickupItem.x - (pose.nearArm.wrist.x + 18),
          pose.activityState.pickupItem.y - pose.nearArm.wrist.y)
      : 0,
    // Pelvis-to-seat offset is an explicit semantic check, separate from IK.
    // The intended seated pose places the pelvis center about 10px below the seat top.
    seatContactErrorPx: pose.activityState.chair
      ? Math.abs(pose.pelvis.y - (pose.activityState.chair.seatY + 8))
      : null,
    reachTargetContactErrorPx: pose.activityState.reachTarget?.active
      ? Math.hypot(pose.nearArm.wrist.x - pose.activityState.reachTarget.x,
          pose.nearArm.wrist.y - pose.activityState.reachTarget.y)
      : null,
    groundPenetrationPx: Math.max(0, pose.leftFoot.y - scene.background.horizon_y, pose.rightFoot.y - scene.background.horizon_y),
    stance: { left: pose.leftFoot.inStance, right: pose.rightFoot.inStance },
    armMode, activity
  };
  return pose;
}
