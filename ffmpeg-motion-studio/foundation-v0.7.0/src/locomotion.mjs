const TAU = 2 * Math.PI;
const clamp = (v, lo, hi) => Math.min(hi, Math.max(lo, v));
const fract = (v) => v - Math.floor(v);
const dist = (a, b) => Math.hypot(b.x - a.x, b.y - a.y);
const rotatePoint = (point, pivot, radians) => {
  const dx = point.x - pivot.x;
  const dy = point.y - pivot.y;
  const c = Math.cos(radians), s = Math.sin(radians);
  return { x: pivot.x + dx * c - dy * s, y: pivot.y + dx * s + dy * c };
};

function smoothstep(t) {
  const u = clamp(t, 0, 1);
  return u * u * (3 - 2 * u);
}

function solveTwoBoneIK(hip, ankle, upperLength, lowerLength, bendSign = 1) {
  const dx = ankle.x - hip.x;
  const dy = ankle.y - hip.y;
  const rawDistance = Math.hypot(dx, dy);
  const d = clamp(rawDistance, Math.abs(upperLength - lowerLength) + 1e-7, upperLength + lowerLength - 1e-7);
  const theta = rawDistance < 1e-9 ? -Math.PI / 2 : Math.atan2(dy, dx);
  const cosA = clamp((upperLength ** 2 + d ** 2 - lowerLength ** 2) / (2 * upperLength * d), -1, 1);
  const offset = Math.acos(cosA);
  const candidates = [theta + offset, theta - offset].map((a) => ({ x: hip.x + upperLength * Math.cos(a), y: hip.y + upperLength * Math.sin(a) }));
  // Deterministic signed bend prevents branch switches when an endpoint crosses the body axis.
  const knee = bendSign >= 0 ? candidates[0] : candidates[1];
  const solvedAnkle = { x: hip.x + d * Math.cos(theta), y: hip.y + d * Math.sin(theta) };
  return {
    hip: { ...hip }, knee, ankle: solvedAnkle,
    upperError: Math.abs(dist(hip, knee) - upperLength),
    lowerError: Math.abs(dist(knee, solvedAnkle) - lowerLength),
    ankleClampError: dist(ankle, solvedAnkle),
    rawDistance,
  };
}

function footLocalOffset(phase, strideLength, stanceFraction) {
  if (phase < stanceFraction) return strideLength * (stanceFraction / 2 - phase);
  const u = (phase - stanceFraction) / (1 - stanceFraction);
  return -strideLength * stanceFraction / 2 + strideLength * stanceFraction * smoothstep(u);
}

function evaluateFoot(timeSeconds, phaseOffset, scene, rootX) {
  const m = scene.motion;
  const p = fract(timeSeconds / m.cycle_seconds + phaseOffset);
  const inStance = p < m.stance_fraction;
  const swingU = inStance ? 0 : (p - m.stance_fraction) / (1 - m.stance_fraction);
  const x = rootX + footLocalOffset(p, m.stride_length_px, m.stance_fraction);
  const lift = inStance ? 0 : m.swing_lift_px * 16 * swingU * swingU * (1 - swingU) * (1 - swingU);
  const angle = inStance ? 0.015 * Math.sin(Math.PI * p / m.stance_fraction) : 0.11 * Math.sin(Math.PI * 2 * swingU);
  return { phase: p, inStance, swingU, x, y: scene.background.horizon_y - lift, lift, angle };
}

export function evaluateLocomotion(scene, frameIndex) {
  if (!Number.isInteger(frameIndex) || frameIndex < 0 || frameIndex >= scene.duration_frames) {
    throw new RangeError("frameIndex outside declared locomotion timeline");
  }
  const m = scene.motion;
  const c = scene.character;
  const p = frameIndex / scene.fps;
  const cyclePhase = fract(p / m.cycle_seconds);
  const rootX = m.start_x + m.stride_length_px * (p / m.cycle_seconds);
  const pelvisBob = m.pelvis_bob_px * (0.5 - 0.5 * Math.cos(TAU * 2 * cyclePhase));
  const pelvis = { x: rootX, y: m.root_y - pelvisBob };
  const torsoAngle = m.torso_sway_radians * Math.sin(TAU * cyclePhase);
  const headAngle = -0.58 * torsoAngle + 0.007 * Math.sin(TAU * cyclePhase + 0.35);
  const chestLocal = { x: rootX + 2.0 * Math.sin(TAU * cyclePhase + 0.25), y: pelvis.y - 70 };
  const chest = rotatePoint(chestLocal, pelvis, torsoAngle);
  const headLocal = { x: rootX + 2.0 * Math.sin(TAU * cyclePhase + 0.25) + 3, y: m.root_y - 137 - pelvisBob * 0.42 };
  const head = rotatePoint(headLocal, pelvis, torsoAngle * 0.42);
  const neck = rotatePoint({ x: headLocal.x, y: headLocal.y + c.head_radius_px - 2 }, pelvis, torsoAngle * 0.72);
  const shoulders = {
    near: rotatePoint({ x: chestLocal.x + 13, y: chestLocal.y + 5 }, pelvis, torsoAngle),
    far: rotatePoint({ x: chestLocal.x - 10, y: chestLocal.y + 4 }, pelvis, torsoAngle),
  };
  const groundY = scene.background.horizon_y;
  const leftFoot = evaluateFoot(p, 0, scene, rootX);
  const rightFoot = evaluateFoot(p, 0.5, scene, rootX);
  const leftHip = { x: pelvis.x - 11, y: pelvis.y + 2 };
  const rightHip = { x: pelvis.x + 11, y: pelvis.y + 2 };
  const leftLeg = solveTwoBoneIK(leftHip, { x: leftFoot.x, y: leftFoot.y - 3 }, c.upper_leg_px, c.lower_leg_px, -1);
  const rightLeg = solveTwoBoneIK(rightHip, { x: rightFoot.x, y: rightFoot.y - 3 }, c.upper_leg_px, c.lower_leg_px, 1);

  // Prop carry uses stable handle contacts and a reduced-amplitude basket response.
  const basketCenter = {
    x: rootX + 67,
    y: m.root_y - 48 + m.basket_vertical_response_px * Math.sin(TAU * cyclePhase - 0.38),
  };
  const basket = {
    x: basketCenter.x - scene.prop.basket_width_px / 2,
    y: basketCenter.y - scene.prop.basket_height_px / 2,
    width: scene.prop.basket_width_px,
    height: scene.prop.basket_height_px,
    handleLeft: { x: basketCenter.x - 14, y: basketCenter.y - scene.prop.basket_height_px / 2 + 3 },
    handleRight: { x: basketCenter.x + 14, y: basketCenter.y - scene.prop.basket_height_px / 2 + 3 },
  };
  const nearArmRaw = solveTwoBoneIK(shoulders.near, { ...basket.handleLeft }, c.upper_arm_px, c.forearm_px, 1);
  const farArmRaw = solveTwoBoneIK(shoulders.far, { ...basket.handleRight }, c.upper_arm_px, c.forearm_px, 1);
  const nearArm = { ...nearArmRaw, shoulder: nearArmRaw.hip, elbow: nearArmRaw.knee, wrist: nearArmRaw.ankle };
  const farArm = { ...farArmRaw, shoulder: farArmRaw.hip, elbow: farArmRaw.knee, wrist: farArmRaw.ankle };
  const diagnostics = {
    boneLengthErrorPx: Math.max(leftLeg.upperError, leftLeg.lowerError, rightLeg.upperError, rightLeg.lowerError, nearArm.upperError, nearArm.lowerError, farArm.upperError, farArm.lowerError),
    ankleClampErrorPx: Math.max(leftLeg.ankleClampError, rightLeg.ankleClampError),
    basketContactErrorPx: Math.max(dist(nearArm.ankle, basket.handleLeft), dist(farArm.ankle, basket.handleRight)),
    groundPenetrationPx: Math.max(0, leftFoot.y - groundY, rightFoot.y - groundY),
    footPhases: { left: leftFoot.phase, right: rightFoot.phase },
    stance: { left: leftFoot.inStance, right: rightFoot.inStance },
  };
  return {
    frameIndex, timeSeconds: p, cyclePhase, rootX, pelvisBob, pelvis, chest, chestLocal, neck, head, headLocal, torsoAngle, headAngle,
    shoulders, leftFoot, rightFoot, leftHip, rightHip, leftLeg, rightLeg, nearArm, farArm, basket, basketCenter, diagnostics,
  };
}

export function sampleStanceWorldDrift(scene, frameIndex, side, samples = 8) {
  const start = evaluateLocomotion(scene, frameIndex);
  const foot = side === "left" ? start.leftFoot : start.rightFoot;
  if (!foot.inStance) return null;
  const m = scene.motion;
  const remaining = (m.stance_fraction - foot.phase) * m.cycle_seconds;
  const duration = Math.max(0, Math.min(remaining * 0.92, m.cycle_seconds * m.stance_fraction * 0.92));
  const positions = [];
  for (let i = 0; i <= samples; i += 1) {
    const f = Math.min(scene.duration_frames - 1, frameIndex + Math.floor(i * duration * scene.fps / samples));
    const state = evaluateLocomotion(scene, f);
    positions.push(side === "left" ? state.leftFoot.x : state.rightFoot.x);
  }
  return Math.max(...positions) - Math.min(...positions);
}
