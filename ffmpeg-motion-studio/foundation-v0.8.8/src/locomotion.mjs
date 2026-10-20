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
const rotate = (p, pivot, a) => {
  const dx = p.x - pivot.x, dy = p.y - pivot.y, c = Math.cos(a), s = Math.sin(a);
  return { x: pivot.x + dx * c - dy * s, y: pivot.y + dx * s + dy * c };
};

/** Hermite trajectory keeps first derivative continuous at swing/stance boundaries. */
export function footLocalOffset(phase, strideLength, stanceFraction) {
  const p = clamp(phase, 0, 1), sf = clamp(stanceFraction, 0.1, 0.9);
  if (p < sf) return strideLength * (sf / 2 - p);
  const u = clamp((p - sf) / (1 - sf), 0, 1);
  const start = -strideLength * sf / 2, delta = strideLength * sf, tangent = -strideLength * (1 - sf);
  return (u*u*u - 2*u*u + u) * tangent + (-2*u*u*u + 3*u*u) * delta +
         (u*u*u - u*u) * tangent + start;
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

function makeFoot(t, phaseOffset, scene, rootX, depth) {
  const m = scene.motion, phase = fract(t / m.cycle_seconds + phaseOffset);
  const stance = phase < m.stance_fraction, swingU = stance ? 0 : (phase - m.stance_fraction) / (1 - m.stance_fraction);
  const stride = m.stride_length_px * (m.screen_stride_scale || 1);
  const x = rootX + footLocalOffset(phase, stride, m.stance_fraction) + depth;
  const lift = stance ? 0 : m.swing_lift_px * 16 * swingU*swingU*(1-swingU)*(1-swingU);
  let angle;
  if (stance) {
    const q = phase / m.stance_fraction;
    angle = q < 0.1 ? -m.heel_toe_roll_radians * (1 - q/0.1) :
      q > 0.82 ? m.heel_toe_roll_radians * (q - 0.82)/0.18 : 0;
  } else angle = m.heel_toe_roll_radians * (1 - 2 * smoothstep(swingU));
  return { phase, inStance: stance, swingU, x, y: scene.background.horizon_y - lift, lift, angle };
}
const armPack = (ik, shoulder, wrist) => ({
  ...ik, shoulder: { ...shoulder }, elbow: ik.joint, elbowAngleDegrees: ik.jointAngleDegrees,
  wrist: ik.end, target: { ...wrist }
});

export function evaluateLocomotion(scene, frameIndex, armMode = scene.motion.arm_mode || "carry") {
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= scene.duration_frames) throw new RangeError("Frame is outside timeline.");
  if (armMode !== "carry" && armMode !== "free") throw new RangeError("Unsupported arm mode.");
  const m = scene.motion, c = scene.character, p = frameIndex / scene.fps, cycle = fract(p / m.cycle_seconds);
  const projected = m.stride_length_px * (m.screen_stride_scale || 1);
  const rootX = m.start_x + projected * (p / m.cycle_seconds);
  const bob = m.pelvis_bob_px * (0.5 - 0.5 * Math.cos(TAU * 2 * cycle));
  const pelvis = { x: rootX, y: m.root_y - bob };
  const torsoAngle = m.torso_sway_radians * Math.sin(TAU * cycle) + (m.secondary_torso_sway_radians || 0.018) * Math.sin(TAU * 2 * cycle + 0.48);
  const headAngle = -0.72 * torsoAngle + (m.head_follow_radians || 0.018) * Math.sin(TAU * cycle + 0.35) + (m.head_bob_radians || 0.008) * Math.sin(TAU * 2 * cycle - 0.4);
  const chestLocal = { x: rootX + (m.torso_shift_px || 4.5) * Math.sin(TAU * cycle + 0.25), y: pelvis.y - (m.torso_length_px || 70) };
  const chest = rotate(chestLocal, pelvis, torsoAngle);
  const headLocal = { x: chestLocal.x + (m.head_follow_x_px || 3.5), y: m.root_y - (m.head_center_offset_y_px || 137) - bob * 0.5 };
  const head = rotate(headLocal, pelvis, torsoAngle * 0.42);
  const neck = rotate({ x: headLocal.x, y: headLocal.y + c.head_radius_px * 0.82 }, pelvis, torsoAngle * 0.72);
  const shoulders = {
    near: rotate({ x: chestLocal.x + (c.shoulder_half_width_px || 15), y: chestLocal.y + 6 }, pelvis, torsoAngle),
    far: rotate({ x: chestLocal.x - (c.shoulder_half_width_px || 7), y: chestLocal.y + 7 }, pelvis, torsoAngle)
  };
  const depth = c.leg_depth_projection_px || 0;
  const leftFoot = makeFoot(p, 0, scene, rootX, depth), rightFoot = makeFoot(p, 0.5, scene, rootX, -depth);
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
    x: rootX + m.basket_offset_x_px,
    y: m.root_y + m.basket_center_offset_y_px - bob * 0.25 + m.basket_vertical_response_px * Math.sin(TAU * cycle - 0.42)
  };
  const half = scene.prop.handle_spacing_px / 2;
  const basketAngle = (m.basket_tilt_radians || 0.045) * Math.sin(TAU * cycle - (m.basket_tilt_phase_radians || 0.42));
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
    const amp = m.free_arm_swing_px;
    const nearPhase = TAU * (cycle + 0.5), farPhase = TAU * cycle, verticalAmp = m.free_arm_vertical_swing_px || 9;
    nearWrist = { x: shoulders.near.x + amp * Math.sin(nearPhase), y: shoulders.near.y + m.free_arm_drop_px + verticalAmp * Math.cos(nearPhase + 0.2) };
    farWrist = { x: shoulders.far.x + amp * Math.sin(farPhase), y: shoulders.far.y + m.free_arm_drop_px + verticalAmp * Math.cos(farPhase + 0.2) };
    nearPole = { x: (shoulders.near.x + nearWrist.x) / 2 - 12, y: (shoulders.near.y + nearWrist.y) / 2 + 3 };
    farPole = { x: (shoulders.far.x + farWrist.x) / 2 - 12, y: (shoulders.far.y + farWrist.y) / 2 + 3 };
  }
  const na = solveTwoBoneIK(shoulders.near, nearWrist, c.upper_arm_px, c.forearm_px, nearPole, -1);
  const fa = solveTwoBoneIK(shoulders.far, farWrist, c.upper_arm_px, c.forearm_px, farPole, -1);
  const nearArm = armPack(na, shoulders.near, nearWrist), farArm = armPack(fa, shoulders.far, farWrist);
  const boneErrors = [leftLeg.upperErrorPx, leftLeg.lowerErrorPx, rightLeg.upperErrorPx, rightLeg.lowerErrorPx,
    nearArm.upperErrorPx, nearArm.lowerErrorPx, farArm.upperErrorPx, farArm.lowerErrorPx];
  return {
    frameIndex, timeSeconds: p, cyclePhase: cycle, rootX, pelvisBob: bob, pelvis, chest, chestLocal, neck, head,
    headLocal, torsoAngle, headAngle, shoulders, leftFoot, rightFoot, leftHip, rightHip, leftLeg, rightLeg,
    nearArm, farArm, basket, basketCenter,
    diagnostics: {
      boneLengthErrorPx: Math.max(...boneErrors),
      ankleClampErrorPx: Math.max(leftLeg.endpointClampErrorPx, rightLeg.endpointClampErrorPx),
      basketContactErrorPx: armMode === "carry" ? Math.max(dist(nearArm.wrist, basket.handleRight), dist(farArm.wrist, basket.handleLeft)) : 0,
      groundPenetrationPx: Math.max(0, leftFoot.y - scene.background.horizon_y, rightFoot.y - scene.background.horizon_y),
      footPhases: { left: leftFoot.phase, right: rightFoot.phase },
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
