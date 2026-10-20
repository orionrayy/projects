const TAU = 2 * Math.PI;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const fract = (v) => v - Math.floor(v);
const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);
const angleDegrees = (root, joint, end) => {
  const ax = root.x - joint.x, ay = root.y - joint.y;
  const bx = end.x - joint.x, by = end.y - joint.y;
  const den = Math.hypot(ax, ay) * Math.hypot(bx, by);
  return den < 1e-9 ? 0 : Math.acos(clamp((ax * bx + ay * by) / den, -1, 1)) * 180 / Math.PI;
};
const smoothstep = (t) => { const u = clamp(t, 0, 1); return u * u * (3 - 2 * u); };
const smootherstep = (t) => { const u = clamp(t, 0, 1); return u * u * u * (u * (u * 6 - 15) + 10); };
const smootherstepDerivative = (t) => { const u = clamp(t, 0, 1); return 30 * u * u * (1-u) * (1-u); };
function deterministicCycleNoise(index, seed) {
  const x = Math.sin((index + 1) * 12.9898 + seed * 78.233) * 43758.5453;
  return (x - Math.floor(x)) * 2 - 1;
}
function smoothCycleVariation(cycles, seed = 1) {
  const k = Math.floor(cycles), u = fract(cycles), w = smootherstep(u);
  const a = deterministicCycleNoise(k, seed), b = deterministicCycleNoise(k + 1, seed);
  return a + (b - a) * w;
}
function contactPulse(phase, width = 0.09) {
  const p = fract(phase), d = Math.min(p, 1 - p), sigma = Math.max(width, 0.001);
  return Math.exp(-0.5 * (d / sigma) ** 2);
}
function gaitClock(scene, seconds) {
  const duration = scene.duration_frames / scene.fps, m = scene.motion;
  const start = clamp(m.start_ramp_seconds || 0, 0, duration * 0.4);
  const stop = clamp(m.stop_ramp_seconds || 0, 0, duration * 0.4);
  let effectiveSeconds, rate;
  if (start > 0 && seconds < start) {
    const u = clamp(seconds / start, 0, 1);
    effectiveSeconds = start * (u ** 3 - 0.5 * u ** 4);
    rate = smoothstep(u) / m.cycle_seconds;
  } else if (stop > 0 && seconds > duration - stop) {
    const u = clamp((seconds - (duration - stop)) / stop, 0, 1);
    effectiveSeconds = start * 0.5 + Math.max(0, duration - start - stop) + stop * (u - u ** 3 + 0.5 * u ** 4);
    rate = (1 - smoothstep(u)) / m.cycle_seconds;
  } else {
    effectiveSeconds = start * 0.5 + (seconds - start);
    rate = 1 / m.cycle_seconds;
  }
  const baseCycles = effectiveSeconds / m.cycle_seconds;
  const cycleVariation = smoothCycleVariation(baseCycles, 1);
  const cycleIndex = Math.floor(baseCycles), cycleU = fract(baseCycles);
  const phaseNoise = (smoothCycleVariation(baseCycles, 2) - deterministicCycleNoise(0, 2)) / 2;
  const phaseNoiseSlope = (deterministicCycleNoise(cycleIndex + 1, 2) - deterministicCycleNoise(cycleIndex, 2)) * smootherstepDerivative(cycleU) / 2;
  const phaseVariationCycles = m.phase_variation_cycles || 0;
  const phaseCoordinateCycles = baseCycles + phaseVariationCycles * phaseNoise;
  const phaseRate = rate * (1 + phaseVariationCycles * phaseNoiseSlope);
  return { cycles: phaseCoordinateCycles, phaseCoordinateCycles, baseCycles, rateCyclesPerSecond: phaseRate, cycleVariation, effectiveSeconds };
}
function armHorizontalWave(phase) {
  return Math.sin(TAU * phase) + 0.14 * Math.sin(2 * TAU * phase - 0.55) + 0.035 * Math.sin(3 * TAU * phase + 0.28);
}
function armVerticalWave(phase) {
  return Math.cos(TAU * phase + 0.18) + 0.16 * Math.cos(2 * TAU * phase - 0.42);
}
const rotate = (p, pivot, a) => {
  const dx = p.x - pivot.x, dy = p.y - pivot.y, c = Math.cos(a), s = Math.sin(a);
  return { x: pivot.x + dx * c - dy * s, y: pivot.y + dx * s + dy * c };
};

/** Quintic Hermite trajectory matches position, velocity and acceleration at stance/swing boundaries. */
export function footLocalOffset(phase, strideLength, stanceFraction) {
  const p = clamp(phase, 0, 1), sf = clamp(stanceFraction, 0.1, 0.9);
  if (p < sf) return strideLength * (sf / 2 - p);
  const u = clamp((p - sf) / (1 - sf), 0, 1);
  const start = -strideLength * sf / 2, delta = strideLength * sf, tangent = -strideLength * (1 - sf);
  const correction = delta - tangent;
  const u2 = u * u, u3 = u2 * u, u4 = u3 * u, u5 = u4 * u;
  return start + tangent * u + correction * (10 * u3 - 15 * u4 + 6 * u5);
}

/** Analytic two-bone IK with an explicit 2D pole target and bounded unreachable-target clamp. */
export function solveTwoBoneIK(root, target, upperLength, lowerLength, poleTarget = null, bendSign = 1) {
  if (![root.x, root.y, target.x, target.y, upperLength, lowerLength].every(Number.isFinite) ||
      upperLength <= 0 || lowerLength <= 0) throw new TypeError("IK values must be finite and lengths positive");
  const dx = target.x - root.x, dy = target.y - root.y, raw = Math.hypot(dx, dy);
  const reach = clamp(raw, Math.abs(upperLength - lowerLength) + 1e-7, upperLength + lowerLength - 1e-7);
  const theta = raw < 1e-9 ? -Math.PI / 2 : Math.atan2(dy, dx);
  const offset = Math.acos(clamp((upperLength*upperLength + reach*reach - lowerLength*lowerLength) /
                                 (2 * upperLength * reach), -1, 1));
  const candidates = [theta + offset, theta - offset].map(a => ({
    x: root.x + upperLength * Math.cos(a), y: root.y + upperLength * Math.sin(a)
  }));
  let joint;
  if (poleTarget && Number.isFinite(poleTarget.x) && Number.isFinite(poleTarget.y)) {
    const score = p => (p.x - poleTarget.x) ** 2 + (p.y - poleTarget.y) ** 2;
    joint = score(candidates[0]) <= score(candidates[1]) ? candidates[0] : candidates[1];
  } else joint = candidates[bendSign >= 0 ? 0 : 1];
  const end = { x: root.x + reach * Math.cos(theta), y: root.y + reach * Math.sin(theta) };
  return {
    root: { ...root }, joint, end,
    upperErrorPx: Math.abs(dist(root, joint) - upperLength),
    lowerErrorPx: Math.abs(dist(joint, end) - lowerLength),
    endpointClampErrorPx: dist(target, end),
    jointAngleDegrees: angleDegrees(root, joint, end),
    requestedReachPx: raw, solvedReachPx: reach
  };
}

function makeFoot(cycleCoordinate, phaseOffset, scene, rootX, depth, swingScale = 1, cycleVariation = 0) {
  const m = scene.motion, phase = fract(cycleCoordinate + phaseOffset);
  const stance = phase < m.stance_fraction, swingU = stance ? 0 : (phase - m.stance_fraction) / (1 - m.stance_fraction);
  const stride = m.stride_length_px * (m.screen_stride_scale || 1);
  const x = rootX + footLocalOffset(phase, stride, m.stance_fraction) + depth;
  const liftPulse = stance ? 0 : 64 * swingU*swingU*swingU*(1-swingU)*(1-swingU)*(1-swingU);
  const lift = m.swing_lift_px * swingScale * (1 + (m.cycle_lift_variation_fraction || 0) * cycleVariation) * liftPulse;
  const roll = m.heel_toe_roll_radians;
  let angle;
  if (stance) {
    const q = phase / m.stance_fraction;
    if (q < 0.12) angle = -roll * (1 - smootherstep(q / 0.12));
    else if (q > 0.84) angle = roll * smootherstep((q - 0.84) / 0.16);
    else angle = 0;
  } else angle = roll * (1 - 2 * smootherstep(swingU));
  return { phase, inStance: stance, swingU, x, y: scene.background.horizon_y - lift, lift, angle };
}
const armPack = (ik, shoulder, wrist) => ({
  ...ik, shoulder: { ...shoulder }, elbow: ik.joint, elbowAngleDegrees: ik.jointAngleDegrees,
  wrist: ik.end, target: { ...wrist }
});

export function evaluateLocomotion(scene, frameIndex, armMode = scene.motion.arm_mode || "carry") {
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= scene.duration_frames) throw new RangeError("Frame is outside timeline.");
  if (armMode !== "carry" && armMode !== "free") throw new RangeError("Unsupported arm mode.");
  const m = scene.motion, c = scene.character, p = frameIndex / scene.fps;
  const gait = gaitClock(scene, p), cycleCoordinate = gait.cycles, cycle = fract(cycleCoordinate), cycleVariation = gait.cycleVariation;
  const projected = m.stride_length_px * (m.screen_stride_scale || 1);
  const rootX = m.start_x + projected * cycleCoordinate;
  const responseWidth = m.contact_response_width_cycles || 0.09;
  const leftImpact = contactPulse(cycle, responseWidth), rightImpact = contactPulse(cycle + 0.5, responseWidth);
  const contactLoad = leftImpact + rightImpact, contactBalance = leftImpact - rightImpact;
  const bob = m.pelvis_bob_px * (0.5 - 0.5 * Math.cos(TAU * 2 * cycle)) +
    (m.pelvis_bob_asymmetry_px || 0) * (Math.sin(TAU * cycle - 0.25) - Math.sin(-0.25));
  const pelvis = {
    x: rootX + (m.pelvis_lateral_shift_px || 0) * Math.sin(TAU * cycle + 0.72) + (m.contact_lateral_shift_px || 0) * contactBalance,
    y: m.root_y - bob + (m.contact_compression_px || 0) * contactLoad
  };
  const torsoAngle = (m.torso_forward_lean_radians || 0) + m.torso_sway_radians * Math.sin(TAU * cycle) +
    (m.secondary_torso_sway_radians || 0) * Math.sin(TAU * 2 * cycle + 0.48) +
    (m.contact_torso_reaction_radians || 0) * contactBalance +
    cycleVariation * (m.cycle_torso_sway_variation_radians || 0);
  const headAngle = -0.72 * torsoAngle +
    (m.head_follow_radians || 0) * Math.sin(TAU * cycle + 0.35) +
    (m.head_bob_radians || 0) * Math.sin(TAU * 2 * cycle - 0.4) -
    (m.contact_head_counter_radians || 0) * contactBalance;
  const chestLocal = {
    x: pelvis.x + (m.torso_shift_px || 0) * Math.sin(TAU * cycle + 0.25) +
      (m.contact_chest_shift_px || 0) * contactBalance + (m.cycle_torso_shift_variation_px || 0) * cycleVariation,
    y: pelvis.y - (m.torso_length_px || 70)
  };
  const chest = rotate(chestLocal, pelvis, torsoAngle);
  const headLocal = {
    x: chestLocal.x + (m.head_follow_x_px || 0),
    y: pelvis.y - (m.head_center_offset_y_px || 137) + bob * 0.5 - (m.contact_head_drop_px || 0) * contactLoad
  };
  const head = rotate(headLocal, pelvis, torsoAngle * 0.42);
  const neck = rotate({ x: headLocal.x, y: headLocal.y + c.head_radius_px * 0.82 }, pelvis, torsoAngle * 0.72);
  const shoulders = {
    near: rotate({ x: chestLocal.x + (c.shoulder_depth_projection_px ?? 5), y: chestLocal.y + 6 }, pelvis, torsoAngle),
    far: rotate({ x: chestLocal.x - (c.shoulder_depth_projection_px ?? 5), y: chestLocal.y + 7 }, pelvis, torsoAngle)
  };
  const depth = c.leg_depth_projection_px || 0;
  const leftFoot = makeFoot(cycleCoordinate, 0, scene, rootX, depth, 1.02, cycleVariation);
  const rightFoot = makeFoot(cycleCoordinate, 0.5, scene, rootX, -depth, 0.97, cycleVariation);
  const leftHip = { x: pelvis.x + depth, y: pelvis.y + 2 }, rightHip = { x: pelvis.x - depth, y: pelvis.y + 2 };
  const leftAnkle = { x: leftFoot.x, y: leftFoot.y - 3 }, rightAnkle = { x: rightFoot.x, y: rightFoot.y - 3 };
  // Bias knee extension by contact phase. The squared-sine envelope reaches
  // zero at both ends of swing; smoothstep avoids a pole-target jump at contact.
  const pole = (hip, ankle, foot) => {
    const swingEnvelope = foot.inStance ? 0 : smoothstep(Math.sin(Math.PI * foot.swingU) ** 2);
    const forwardRatio = c.stance_knee_forward_ratio ?? 0.42;
    const upwardRatio = c.stance_knee_up_ratio ?? 0.25;
    const forwardBias = c.knee_forward_bias_px * (forwardRatio + (1 - forwardRatio) * swingEnvelope);
    const upwardBias = c.knee_up_bias_px * (upwardRatio + (1 - upwardRatio) * swingEnvelope);
    return {
      x: (hip.x + ankle.x) / 2 + forwardBias,
      y: (hip.y + ankle.y) / 2 - upwardBias
    };
  };
  const l = solveTwoBoneIK(leftHip, leftAnkle, c.upper_leg_px, c.lower_leg_px, pole(leftHip, leftAnkle, leftFoot), -1);
  const r = solveTwoBoneIK(rightHip, rightAnkle, c.upper_leg_px, c.lower_leg_px, pole(rightHip, rightAnkle, rightFoot), -1);
  const leftLeg = { ...l, hip: leftHip, knee: l.joint, ankle: l.end };
  const rightLeg = { ...r, hip: rightHip, knee: r.joint, ankle: r.end };

  const basketCenter = {
    x: pelvis.x + m.basket_offset_x_px,
    y: pelvis.y + m.basket_center_offset_y_px + m.basket_vertical_response_px * Math.sin(TAU * cycle - 0.42) + (m.contact_basket_response_px || 0) * contactLoad
  };
  const half = scene.prop.handle_spacing_px / 2;
  const basketAngle = (m.basket_tilt_radians || 0) * Math.sin(TAU * cycle - (m.basket_tilt_phase_radians || 0.42)) + (m.contact_basket_tilt_radians || 0) * contactBalance;
  const handleLeftLocal = { x: basketCenter.x - half, y: basketCenter.y - scene.prop.basket_height_px / 2 + 4 };
  const handleRightLocal = { x: basketCenter.x + half, y: basketCenter.y - scene.prop.basket_height_px / 2 + 4 };
  const basket = {
    x: basketCenter.x - scene.prop.basket_width_px / 2,
    y: basketCenter.y - scene.prop.basket_height_px / 2,
    width: scene.prop.basket_width_px, height: scene.prop.basket_height_px,
    center: { ...basketCenter },
    angleRadians: basketAngle,
    angleDegrees: basketAngle * 180 / Math.PI,
    handleLeft: rotate(handleLeftLocal, basketCenter, basketAngle),
    handleRight: rotate(handleRightLocal, basketCenter, basketAngle)
  };
  let nearWrist, farWrist, nearPole, farPole;
  if (armMode === "carry") {
    nearWrist = { ...basket.handleRight }; farWrist = { ...basket.handleLeft };
    nearPole = { x: (shoulders.near.x + nearWrist.x) / 2 - 3, y: (shoulders.near.y + nearWrist.y) / 2 + 15 };
    farPole = { x: (shoulders.far.x + farWrist.x) / 2 + 5, y: (shoulders.far.y + farWrist.y) / 2 + 13 };
  } else {
    const amp = m.free_arm_swing_px, armLag = m.arm_lag_cycles || 0.035;
    const nearPhase = fract(cycle + 0.5 - armLag), farPhase = fract(cycle - armLag);
    const verticalAmp = m.free_arm_vertical_swing_px || 0;
    const armScale = 1 + cycleVariation * (m.cycle_arm_variation_fraction || 0);
    const armCounter = (m.contact_arm_reaction_px || 0) * contactBalance;
    nearWrist = {
      x: shoulders.near.x + amp * armHorizontalWave(nearPhase) * armScale + armCounter,
      y: shoulders.near.y + m.free_arm_drop_px + verticalAmp * armVerticalWave(nearPhase) * armScale + contactBalance * 0.3
    };
    farWrist = {
      x: shoulders.far.x + amp * armHorizontalWave(farPhase) * armScale - armCounter,
      y: shoulders.far.y + m.free_arm_drop_px + verticalAmp * armVerticalWave(farPhase) * armScale - contactBalance * 0.3
    };
    nearPole = { x: (shoulders.near.x + nearWrist.x) / 2 - 12, y: (shoulders.near.y + nearWrist.y) / 2 + 3 };
    farPole = { x: (shoulders.far.x + farWrist.x) / 2 - 12, y: (shoulders.far.y + farWrist.y) / 2 + 3 };
  }
  const na = solveTwoBoneIK(shoulders.near, nearWrist, c.upper_arm_px, c.forearm_px, nearPole, -1);
  const fa = solveTwoBoneIK(shoulders.far, farWrist, c.upper_arm_px, c.forearm_px, farPole, -1);
  const nearArm = armPack(na, shoulders.near, nearWrist), farArm = armPack(fa, shoulders.far, farWrist);
  const boneErrors = [leftLeg.upperErrorPx, leftLeg.lowerErrorPx, rightLeg.upperErrorPx, rightLeg.lowerErrorPx,
    nearArm.upperErrorPx, nearArm.lowerErrorPx, farArm.upperErrorPx, farArm.lowerErrorPx];
  return {
    frameIndex, timeSeconds: p, cyclePhase: cycle, cycleCoordinate, baseCycleCoordinate: gait.baseCycles, cycleVariation, gaitRateCyclesPerSecond: gait.rateCyclesPerSecond,
    rootX, pelvisBob: bob, pelvis, chest, chestLocal, neck, head, headLocal, torsoAngle, headAngle, shoulders,
    leftFoot, rightFoot, leftHip, rightHip, leftLeg, rightLeg, nearArm, farArm, basket, basketCenter,
    diagnostics: {
      boneLengthErrorPx: Math.max(...boneErrors),
      ankleClampErrorPx: Math.max(leftLeg.endpointClampErrorPx, rightLeg.endpointClampErrorPx),
      basketContactErrorPx: armMode === "carry" ? Math.max(dist(nearArm.wrist, basket.handleRight), dist(farArm.wrist, basket.handleLeft)) : 0,
      groundPenetrationPx: Math.max(0, leftFoot.y - scene.background.horizon_y, rightFoot.y - scene.background.horizon_y),
      footPhases: { left: leftFoot.phase, right: rightFoot.phase },
      contactLoad, contactBalance, cycleVariation, gaitRateCyclesPerSecond: gait.rateCyclesPerSecond,
      stance: { left: leftFoot.inStance, right: rightFoot.inStance }, armMode
    }
  };
}
export function sampleStanceWorldDrift(scene, frameIndex, side, samples = 8, armMode = scene.motion.arm_mode || "carry") {
  const start = evaluateLocomotion(scene, frameIndex, armMode), foot = side === "left" ? start.leftFoot : start.rightFoot;
  if (!foot.inStance) return null;
  const m = scene.motion, remaining = (m.stance_fraction - foot.phase) * m.cycle_seconds;
  const duration = Math.max(0, Math.min(remaining * 0.92, m.cycle_seconds * m.stance_fraction * 0.92));
  const positions = [];
  for (let i = 0; i <= samples; i++) {
    const f = Math.min(scene.duration_frames - 1, frameIndex + Math.floor(i * duration * scene.fps / samples));
    const s = evaluateLocomotion(scene, f, armMode);
    positions.push(side === "left" ? s.leftFoot.x : s.rightFoot.x);
  }
  return Math.max(...positions) - Math.min(...positions);
}
