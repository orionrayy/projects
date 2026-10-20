import { evaluateLocomotion, solveTwoBoneIK } from "./locomotion.mjs";

const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const smoothstep = (t) => { const u = clamp(t, 0, 1); return u * u * (3 - 2 * u); };
const TAU = Math.PI * 2;

export const ACTIVITY_NAMES = Object.freeze([
  "stand", "look-around", "reach", "pick-up", "sit-to-stand", "turn-in-place"
]);
export const ACTIVITY_LABELS = Object.freeze({
  "stand": "STAND / BREATH",
  "look-around": "HEAD TILT + GAZE / 2D PROFILE",
  "reach": "REACH FORWARD",
  "pick-up": "CROUCH / PICK UP",
  "sit-to-stand": "SIT TO STAND",
  "turn-in-place": "WEIGHT SHIFT / FOOT PIVOT"
});

function pulse(u, rise = 0.2, fall = 0.78) {
  return smoothstep(u / rise) * (1 - smoothstep((u - fall) / (1 - fall)));
}

// Shape-preserving cubic interpolation for action channels. Unlike long pulse holds
// or independent ease-in/ease-out segments, this preserves velocity continuity at
// ordinary keys and prevents overshoot at contact/extrema keys.
function keyCurve(u, keys) {
  if (u <= keys[0][0]) return keys[0][1];
  if (u >= keys[keys.length - 1][0]) return keys[keys.length - 1][1];
  const slopes = [];
  for (let i = 0; i < keys.length - 1; i++) {
    slopes.push((keys[i + 1][1] - keys[i][1]) / (keys[i + 1][0] - keys[i][0]));
  }
  const tangent = (i) => {
    if (i === 0) return slopes[0];
    if (i === keys.length - 1) return slopes[slopes.length - 1];
    const a = slopes[i - 1], b = slopes[i];
    if (a === 0 || b === 0 || Math.sign(a) !== Math.sign(b)) return 0;
    const h0 = keys[i][0] - keys[i - 1][0];
    const h1 = keys[i + 1][0] - keys[i][0];
    const w1 = 2 * h1 + h0, w2 = h1 + 2 * h0;
    return (w1 + w2) / (w1 / a + w2 / b);
  };
  let i = 0;
  while (i < keys.length - 2 && u > keys[i + 1][0]) i++;
  const [x0, y0] = keys[i], [x1, y1] = keys[i + 1];
  const h = x1 - x0, t = (u - x0) / h, t2 = t * t, t3 = t2 * t;
  const value = (2*t3 - 3*t2 + 1)*y0 + (t3 - 2*t2 + t)*h*tangent(i)
    + (-2*t3 + 3*t2)*y1 + (t3 - t2)*h*tangent(i + 1);
  return clamp(value, Math.min(y0, y1), Math.max(y0, y1));
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
      free_arm_drop_px: 100, basket_vertical_response_px: 0, basket_tilt_radians: 0, arm_mode: armMode
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
  // Static side-profile actions need a small depth cue for the two feet; zero stride
  // otherwise projects both shoes and both leg chains onto almost the same pixels.
  base.leftFoot = { ...base.leftFoot, x: base.leftFoot.x - 10 };
  base.rightFoot = { ...base.rightFoot, x: base.rightFoot.x + 10 };
  const duration = Math.max(1, scene.duration_frames - 1);
  const u = frameIndex / duration;
  // Action timelines are authored as explicit phases. The 3 s clip is a preview
  // duration, not permission to hold one pose for most of the sequence.
  const turnPulse = keyCurve(u, [[0,0],[0.12,0],[0.30,1],[0.43,0.82],[0.60,-0.62],[0.72,-0.62],[0.90,0],[1,0]]);
  const pickupCrouch = keyCurve(u, [[0,0],[0.04,0],[0.14,0.48],[0.28,1],[0.37,1],[0.54,0.28],[0.68,0],[1,0]]);
  const pickupReach = keyCurve(u, [[0,0],[0.04,0],[0.14,0.45],[0.27,1],[0.36,1],[0.47,0.58],[0.60,0],[1,0]]);
  const pickupGrip = keyCurve(u, [[0,0],[0.27,0],[0.32,0.90],[0.35,1],[1,1]]);
  const pickupLift = keyCurve(u, [[0,0],[0.36,0],[0.47,0.22],[0.60,1],[1,1]]);
  const pickupTableTopY = scene.background.horizon_y - 144;
  const pickupOrigin = { x: base.shoulders.near.x + 50, y: pickupTableTopY - 13 };
  const pickupTarget = { x: pickupOrigin.x - 18, y: pickupOrigin.y };
  let drop = 0, forwardShift = 0, lean = 0, headTurn = 0, headShift = 0, reachWeight = 0, breath = 0;
  let gazeOffsetX = 0, gazeOffsetY = 0, armCounterBalance = 0, sitStandRestWeight = 0;

  if (activity === "stand") {
    breath = 1.7 * Math.sin(TAU * 0.78 * u);
    lean = 0.012 * Math.sin(TAU * 0.78 * u + 0.4);
  }
  if (activity === "look-around") {
    // A side-profile rig can scan its pitch/tilt and gaze offset; it cannot perform
    // true horizontal yaw. Keep the label explicit and give each glance a clear beat.
    headTurn = keyCurve(u, [[0,0],[0.08,0],[0.24,0.58],[0.34,0.64],[0.46,0.50],[0.58,-0.55],[0.69,-0.62],[0.82,0.12],[0.93,0],[1,0]]);
    headShift = keyCurve(u, [[0,0],[0.20,10],[0.38,11],[0.56,-8],[0.74,-6],[0.90,0],[1,0]]);
    gazeOffsetX = keyCurve(u, [[0,0],[0.16,0],[0.28,1.8],[0.42,1.8],[0.55,-1.8],[0.67,-1.8],[0.82,1.0],[0.92,0],[1,0]]);
    gazeOffsetY = keyCurve(u, [[0,0],[0.24,0.4],[0.38,-0.8],[0.60,0.8],[0.75,0],[1,0]]);
    lean = keyCurve(u, [[0,0],[0.28,0.045],[0.55,-0.035],[0.78,0],[1,0]]);
  }
  if (activity === "reach") {
    reachWeight = keyCurve(u, [[0,0],[0.10,0],[0.22,0.12],[0.40,0.90],[0.46,1],[0.62,1],[0.75,0.62],[0.90,0],[1,0]]);
    lean = 0.075 * reachWeight;
    forwardShift = 3.5 * reachWeight;
  }
  if (activity === "pick-up") {
    drop = 30 * pickupCrouch;
    forwardShift = 10 * pickupCrouch;
    lean = 0.34 * pickupCrouch;
    headTurn = 0.14 * pickupReach;
    gazeOffsetX = 0.60 * pickupReach;
    gazeOffsetY = 0.45 * pickupReach;
    reachWeight = pickupReach;
  }
  if (activity === "sit-to-stand") {
    // Start in a genuinely seated configuration, lean forward before seat-off,
    // then extend and spend the final portion stabilizing upright.
    drop = keyCurve(u, [[0,25],[0.12,25],[0.25,25],[0.38,24],[0.49,18],[0.66,3],[0.80,0],[0.90,0],[1,0]]);
    forwardShift = keyCurve(u, [[0,0],[0.14,0],[0.30,7],[0.40,12],[0.52,10],[0.70,4],[0.86,0],[1,0]]);
    lean = keyCurve(u, [[0,0.02],[0.14,0.02],[0.29,0.20],[0.40,0.34],[0.50,0.28],[0.65,0.12],[0.80,0],[1,0]]);
    armCounterBalance = keyCurve(u, [[0,0],[0.16,0],[0.30,0.62],[0.42,1],[0.55,0.76],[0.72,0.24],[0.88,0],[1,0]]);
    sitStandRestWeight = keyCurve(u, [[0,0],[0.28,0],[0.43,0],[0.56,0.16],[0.72,0.72],[0.86,1],[1,1]]);
  }
  if (activity === "turn-in-place") {
    // This is an explicit 2D weight-shift/foot-pivot cue, not a true 3D turn.
    lean = 0.18 * turnPulse;
    headTurn = -0.38 * turnPulse;
    forwardShift = 15 * turnPulse;
    armCounterBalance = Math.abs(turnPulse);
  }

  const oldPelvis = { ...base.pelvis };
  // Breathing/settling are upper-body-only secondary motion: root and planted feet
  // remain stable. Held-prop and post-rise holds should not freeze into a repeated still frame.
  const pickupCarryBreath = activity === "pick-up" ? pickupLift * 2.0 * Math.sin(TAU * 1.15 * u + 0.2) : 0;
  const chestBreath = activity === "stand" ? breath : pickupCarryBreath;
  const respiratorySway = activity === "stand"
    ? 0.65 * Math.sin(TAU * 0.78 * u + 0.25)
    : activity === "pick-up"
      ? 1.1 * pickupLift * Math.sin(TAU * 1.15 * u + 0.6)
      : activity === "sit-to-stand"
        ? 0.55 * sitStandRestWeight * Math.sin(TAU * 1.2 * u + 0.3)
        : 0;
  const postRiseSettle = activity === "sit-to-stand" && u >= 0.80
    ? 2.0 * Math.sin(Math.PI * (u - 0.80) / 0.20) * Math.exp(-6 * (u - 0.80))
    : 0;
  const newPelvis = { x: oldPelvis.x + forwardShift, y: oldPelvis.y + drop };
  const transform = (pt, factor = 1, ex = 0, ey = 0) =>
    transformUpper(pt, oldPelvis, newPelvis, lean * factor, ex, ey);
  const pose = { ...base,
    activityName: activity, activityProgress: u,
    activityState: { pelvisDropPx: drop, torsoLeanRadians: lean, headTurnRadians: headTurn,
      reachWeight, reachDisplacementPx: 76 * reachWeight, breathingOffsetPx: breath,
      respiratorySwayPx: respiratorySway,
      gazeOffsetX, gazeOffsetY,
      pickupReachWeight: activity === "pick-up" ? pickupReach : 0,
      pickupGripWeight: activity === "pick-up" ? pickupGrip : 0,
      pickupLiftWeight: activity === "pick-up" ? pickupLift : 0,
      armCounterBalanceWeight: armCounterBalance,
      sitStandRestWeight,
      pickupItem: null, chair: null, reachTarget: null },
    pelvis: newPelvis, rootX: newPelvis.x, torsoAngle: lean,
    chestLocal: transform(base.chestLocal, 1, respiratorySway, -chestBreath * 0.82 - postRiseSettle * 0.65),
    chest: transform(base.chest, 1, respiratorySway, -chestBreath * 0.82 - postRiseSettle * 0.65),
    neck: transform(base.neck, 0.72, respiratorySway * 0.5, -chestBreath * 0.55 - postRiseSettle * 0.35),
    headLocal: transform(base.headLocal, 0.42, headShift + respiratorySway * 0.25, -chestBreath * 0.35 - postRiseSettle * 0.15),
    head: transform(base.head, 0.42, headShift + respiratorySway * 0.25, -chestBreath * 0.35 - postRiseSettle * 0.15),
    headAngle: base.headAngle + headTurn - lean * 0.18,
    shoulders: {
      near: transform(base.shoulders.near, 1, respiratorySway, -chestBreath * 0.72 - postRiseSettle * 0.58),
      far: transform(base.shoulders.far, 1, respiratorySway, -chestBreath * 0.72 - postRiseSettle * 0.58)
    }
  };

  const footPivot = activity === "turn-in-place" ? 0.42 * turnPulse : 0;
  pose.leftFoot = { ...base.leftFoot, angle: (base.leftFoot.angle || 0) + footPivot };
  pose.rightFoot = { ...base.rightFoot, angle: (base.rightFoot.angle || 0) - footPivot };
  pose.leftHip = translatePoint(base.leftHip, forwardShift, drop);
  pose.rightHip = translatePoint(base.rightHip, forwardShift, drop);
  pose.leftLeg = solveLeg(pose.leftHip, pose.leftFoot, staticScene);
  pose.rightLeg = solveLeg(pose.rightHip, pose.rightFoot, staticScene);

  let nearTarget = transform(base.nearArm.wrist);
  let farTarget = transform(base.farArm.wrist);
  // Neutral projected hands should occupy opposite depth layers instead of collapsing
  // at the pelvis or meeting in front of the torso due to the base gait's arm swing.
  if (["stand", "look-around", "turn-in-place"].includes(activity)) {
    nearTarget = { x: pose.shoulders.near.x + 12, y: pose.shoulders.near.y + 98 };
    farTarget = { x: pose.shoulders.far.x - 10, y: pose.shoulders.far.y + 98 };
  }
  // In a side-profile projection the two relaxed hands need a small near/far
  // separation; otherwise both arms collapse into one wrist at the pelvis.
  if (["stand", "look-around", "turn-in-place"].includes(activity)) {
    nearTarget = { ...nearTarget, x: nearTarget.x + 7 };
    farTarget = { ...farTarget, x: farTarget.x - 7 };
  }
  if (armMode === "carry") {
    const b = base.basket;
    pose.basket = {
      ...b, x: b.x + forwardShift, y: b.y + drop,
      center: translatePoint(b.center, forwardShift, drop),
      handleLeft: translatePoint(b.handleLeft, forwardShift, drop),
      handleRight: translatePoint(b.handleRight, forwardShift, drop)
    };
    nearTarget = { ...pose.basket.handleRight };
    farTarget = { ...pose.basket.handleLeft };
  } else if (activity === "reach") {
    // Target is fixed in world-space; only the wrist travels. A target parented to
    // the moving shoulder made the old contact test self-fulfilling.
    const restTarget = {
      x: pose.shoulders.near.x + (base.nearArm.wrist.x - base.shoulders.near.x),
      y: pose.shoulders.near.y + (base.nearArm.wrist.y - base.shoulders.near.y)
    };
    const targetX = base.shoulders.near.x + 76;
    const targetY = base.shoulders.near.y + 8;
    nearTarget = {
      x: restTarget.x + (targetX - restTarget.x) * reachWeight,
      y: restTarget.y + (targetY - restTarget.y) * reachWeight - 12 * Math.sin(Math.PI * reachWeight)
    };
    farTarget = { x: farTarget.x - 7 * reachWeight, y: farTarget.y - 3 * reachWeight };
  } else if (activity === "pick-up") {
    // The hand meets the parcel's fixed grasp anchor, then the parcel follows the
    // same wrist-relative offset while the arm lifts toward a carry position.
    const reachingTarget = {
      x: base.nearArm.wrist.x + (pickupTarget.x - base.nearArm.wrist.x) * pickupReach,
      y: base.nearArm.wrist.y + (pickupTarget.y - base.nearArm.wrist.y) * pickupReach
        - 9 * Math.sin(Math.PI * pickupReach)
    };
    // Keep the lifted parcel close to the torso instead of carrying it at arm's length.
    const holdingTarget = { x: pose.shoulders.near.x + 12, y: pose.shoulders.near.y + 42 };
    nearTarget = {
      x: reachingTarget.x + (holdingTarget.x - reachingTarget.x) * pickupLift,
      y: reachingTarget.y + (holdingTarget.y - reachingTarget.y) * pickupLift
    };
    farTarget = { x: pose.shoulders.far.x - 10 - 4 * pickupCrouch + 2 * pickupLift,
      y: pose.shoulders.far.y + 84 - 8 * pickupCrouch - 3 * pickupLift };
  } else if (activity === "sit-to-stand") {
    // Separate the seated lap pose, forward counterbalance, and relaxed standing
    // pose. Reusing the generic folded-arm pose made the entire action read as
    // crossed arms rather than a lower-body transfer.
    const counter = armCounterBalance, rest = sitStandRestWeight;
    const lapNear = { x: pose.shoulders.near.x + 38, y: pose.shoulders.near.y + 86 };
    const lapFar = { x: pose.shoulders.far.x - 10, y: pose.shoulders.far.y + 88 };
    const balanceNear = { x: pose.shoulders.near.x + 52, y: pose.shoulders.near.y + 87 };
    const balanceFar = { x: pose.shoulders.far.x - 5, y: pose.shoulders.far.y + 88 };
    const standingNear = { x: pose.shoulders.near.x + 22, y: pose.shoulders.near.y + 75 };
    const standingFar = { x: pose.shoulders.far.x - 10, y: pose.shoulders.far.y + 82 };
    const actionNear = { x: lapNear.x + (balanceNear.x - lapNear.x) * counter,
      y: lapNear.y + (balanceNear.y - lapNear.y) * counter };
    const actionFar = { x: lapFar.x + (balanceFar.x - lapFar.x) * counter,
      y: lapFar.y + (balanceFar.y - lapFar.y) * counter };
    nearTarget = { x: actionNear.x + (standingNear.x - actionNear.x) * rest,
      y: actionNear.y + (standingNear.y - actionNear.y) * rest };
    farTarget = { x: actionFar.x + (standingFar.x - actionFar.x) * rest,
      y: actionFar.y + (standingFar.y - actionFar.y) * rest };
  } else if (activity === "turn-in-place") {
    nearTarget = { x: nearTarget.x + 8 * turnPulse, y: nearTarget.y + 5 * turnPulse };
    farTarget = { x: farTarget.x - 6 * turnPulse, y: farTarget.y + 3 * turnPulse };
  }

  // Keep the far arm behind the torso and use the near-side elbow branch for neutral poses.
  // The old opposing screen-space poles made both forearms converge across the chest.
  const nearBend = ["stand", "look-around", "turn-in-place"].includes(activity) ? 1 : -1;
  const farBend = armMode === "carry" ? 1 : -1;
  pose.nearArm = solveArm(pose.shoulders.near, nearTarget, staticScene, nearBend);
  pose.farArm = solveArm(pose.shoulders.far, farTarget, staticScene, farBend);

  if (activity === "pick-up") {
    const held = { x: pose.nearArm.wrist.x + 18, y: pose.nearArm.wrist.y };
    pose.activityState.pickupItem = {
      x: pickupOrigin.x + (held.x - pickupOrigin.x) * pickupGrip,
      y: pickupOrigin.y + (held.y - pickupOrigin.y) * pickupGrip,
      width: 34, height: 26, tableX: pickupOrigin.x, tableTopY: pickupTableTopY,
      gripWeight: pickupGrip, held: pickupGrip >= 0.999999,
      graspAnchor: { ...pickupTarget }, handOffsetPx: { x: 18, y: 0 }
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
      x: base.shoulders.near.x + 76,
      y: base.shoulders.near.y + 8,
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
    pickupItemContactErrorPx: pose.activityState.pickupItem?.gripWeight >= 0.95
      ? Math.hypot(pose.activityState.pickupItem.x - (pose.nearArm.wrist.x + 18),
          pose.activityState.pickupItem.y - pose.nearArm.wrist.y)
      : 0,
    pickupItemChestDistancePx: pose.activityState.pickupItem
      ? Math.hypot(pose.activityState.pickupItem.x - pose.nearArm.shoulder.x,
          pose.activityState.pickupItem.y - pose.nearArm.shoulder.y)
      : null,
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
