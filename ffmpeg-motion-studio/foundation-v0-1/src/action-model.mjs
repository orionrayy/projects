import { createCharacterRig, suggestElbowPole } from "./character-rig.mjs";

const clamp = (value, low, high) => Math.min(high, Math.max(low, value));
const smoothstep = (t) => {
  const u = clamp(t, 0, 1);
  return u * u * (3 - 2 * u);
};
const bezier = (p0, p1, p2, p3, t) => {
  const u = 1 - t;
  const a = u * u * u;
  const b = 3 * u * u * t;
  const c = 3 * u * t * t;
  const d = t * t * t;
  return {
    x: a * p0.x + b * p1.x + c * p2.x + d * p3.x,
    y: a * p0.y + b * p1.y + c * p2.y + d * p3.y,
  };
};
const unit = (a, b) => {
  const x = b.x - a.x;
  const y = b.y - a.y;
  const length = Math.max(1e-8, Math.hypot(x, y));
  return { x: x / length, y: y / length };
};

export function evaluateAction(scene, frameIndex) {
  const character = scene.character;
  const motion = scene.motion;
  const origin = character.origin;
  const timeSeconds = frameIndex / scene.fps;
  const anticipationEnd = motion.anticipation_seconds;
  const reachEnd = anticipationEnd + motion.reach_seconds;
  const settleDuration = motion.settle_seconds ?? 0.7;
  const settleTime = Math.max(0, timeSeconds - reachEnd);
  const holdTime = Math.max(0, settleTime - settleDuration);

  const anticipationProgress = anticipationEnd > 0
    ? clamp(timeSeconds / anticipationEnd, 0, 1)
    : 1;
  const anticipationWeight = anticipationEnd > 0
    ? Math.sin(Math.PI * anticipationProgress) ** 2
    : 0;
  const reachLinear = clamp((timeSeconds - anticipationEnd) / motion.reach_seconds, 0, 1);
  const reachProgress = smoothstep(reachLinear);
  const isAnticipating = timeSeconds < anticipationEnd;
  const isReaching = timeSeconds >= anticipationEnd && timeSeconds < reachEnd;
  const isSettling = timeSeconds >= reachEnd && settleTime < settleDuration;
  const phase = isAnticipating
    ? "anticipate"
    : isReaching
      ? "reach"
      : isSettling
        ? "settle"
        : "hold";

  let torsoAngle;
  if (timeSeconds < anticipationEnd) {
    torsoAngle = -0.026 * anticipationWeight;
  } else if (timeSeconds < reachEnd) {
    torsoAngle = 0.044 * reachProgress;
  } else {
    torsoAngle = 0.012
      + 0.032 * Math.exp(-motion.settle_decay * settleTime) * Math.cos(8 * settleTime)
      + 0.0025 * Math.sin(2 * Math.PI * 0.72 * holdTime);
  }

  const rootShift = isAnticipating
    ? -motion.anticipation_px * anticipationWeight
    : 1.8 * reachProgress * Math.exp(-4 * settleTime);
  const rig = createCharacterRig(scene, {
    rootX: origin.x + rootShift,
    torsoAngle,
    headNod: -0.012 * anticipationWeight + 0.014 * reachProgress
      + 0.002 * Math.sin(2 * Math.PI * 0.72 * holdTime),
  });

  const target = { x: scene.board.target_x, y: scene.board.target_y };
  const shoulderToTarget = unit(rig.screenRightShoulder, target);
  const contactWrist = {
    x: target.x - shoulderToTarget.x * character.hand_length,
    y: target.y - shoulderToTarget.y * character.hand_length,
  };
  const restWrist = rig.screenRightRestWrist;
  let requestedWrist;
  let settleAmplitudeUsedPx = 0;

  if (isAnticipating) {
    requestedWrist = {
      x: restWrist.x - 9 * anticipationWeight,
      y: restWrist.y - 13 * anticipationWeight,
    };
  } else if (isReaching) {
    const dx = contactWrist.x - restWrist.x;
    const dy = contactWrist.y - restWrist.y;
    requestedWrist = bezier(
      restWrist,
      { x: restWrist.x + dx * 0.22, y: restWrist.y - 28 },
      { x: contactWrist.x - dx * 0.18, y: contactWrist.y - dy * 0.18 },
      contactWrist,
      reachProgress,
    );
  } else if (isSettling) {
    const decay = Math.exp(-motion.settle_decay * settleTime);
    const settleEnvelope = (1 - Math.exp(-8 * settleTime)) * decay;
    settleAmplitudeUsedPx = motion.settle_amplitude_px * settleEnvelope;
    requestedWrist = {
      x: contactWrist.x + settleAmplitudeUsedPx * Math.sin(motion.settle_frequency * settleTime),
      y: contactWrist.y + settleAmplitudeUsedPx * 0.28
        * (1 - Math.cos(motion.settle_frequency * settleTime)),
    };
  } else {
    requestedWrist = { ...contactWrist };
  }

  const leftArm = character.far_arm;
  const screenLeftShoulder = rig.screenLeftShoulder;
  const screenLeftWrist = rig.screenLeftRestWrist;
  const screenLeftElbowPole = suggestElbowPole(
    screenLeftShoulder,
    screenLeftWrist,
    leftArm.upper_arm_length,
    leftArm.elbow_bend,
  );
  const elbowPole = suggestElbowPole(
    rig.screenRightShoulder,
    requestedWrist,
    character.upper_arm_length,
    motion.elbow_bend,
  );

  return {
    frameIndex,
    timeSeconds,
    phase,
    rig,
    target,
    requestedWrist,
    handAngle: Math.atan2(target.y - requestedWrist.y, target.x - requestedWrist.x),
    elbowPole,
    screenLeftShoulder,
    screenLeftWrist,
    screenLeftElbowPole,
    settleAmplitudeUsedPx,
    anticipationWeight,
    reachProgress,
    settleTime,
    holdTime,
    contactWrist,
    restWrist,
  };
}
