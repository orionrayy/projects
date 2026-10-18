// Deterministic frame-index motion kernel; no random or accumulated playback state.
export function clamp(v, lo, hi) {
  return Math.min(hi, Math.max(lo, v));
}

export function lerp(a, b, t) {
  return a + (b - a) * t;
}

export function smoothstep(t) {
  const u = clamp(t, 0, 1);
  return u * u * (3 - 2 * u);
}

export function distance(a, b) {
  return Math.hypot(b.x - a.x, b.y - a.y);
}

export function solveTwoBoneIK(shoulder, requestedWrist, upperLength, lowerLength, bend = 1) {
  if (!(upperLength > 0 && lowerLength > 0)) {
    throw new RangeError("IK lengths must be positive.");
  }

  const dx = requestedWrist.x - shoulder.x;
  const dy = requestedWrist.y - shoulder.y;
  const rawDistance = Math.hypot(dx, dy);
  const minReach = Math.abs(upperLength - lowerLength) + 1e-6;
  const maxReach = upperLength + lowerLength - 1e-6;
  const solvedDistance = clamp(rawDistance, minReach, maxReach);
  const targetAngle = rawDistance < 1e-8 ? 0 : Math.atan2(dy, dx);
  const wrist = {
    x: shoulder.x + Math.cos(targetAngle) * solvedDistance,
    y: shoulder.y + Math.sin(targetAngle) * solvedDistance,
  };
  const cosine = clamp(
    (upperLength * upperLength + solvedDistance * solvedDistance - lowerLength * lowerLength)
      / (2 * upperLength * solvedDistance),
    -1,
    1,
  );
  const elbowAngle = targetAngle + Math.acos(cosine) * (bend >= 0 ? 1 : -1);
  const elbow = {
    x: shoulder.x + upperLength * Math.cos(elbowAngle),
    y: shoulder.y + upperLength * Math.sin(elbowAngle),
  };

  return {
    shoulder: { ...shoulder },
    elbow,
    wrist,
    requestedWrist: { ...requestedWrist },
    requestedDistance: rawDistance,
    actualDistance: solvedDistance,
    reachable: Math.abs(rawDistance - solvedDistance) < 0.02,
    upperError: Math.abs(distance(shoulder, elbow) - upperLength),
    lowerError: Math.abs(distance(elbow, wrist) - lowerLength),
  };
}

export function evaluateFrame(scene, frameIndex) {
  if (!Number.isInteger(frameIndex)) {
    throw new TypeError("frameIndex must be an integer.");
  }
  if (frameIndex < 0 || frameIndex >= scene.duration_frames) {
    throw new RangeError("frameIndex outside declared timeline.");
  }

  const timeSeconds = frameIndex / scene.fps;
  const character = scene.character;
  const motion = scene.motion;
  const board = scene.board;
  const origin = character.origin;
  const anticipationEnd = motion.anticipation_seconds;
  const reachEnd = anticipationEnd + motion.reach_seconds;
  const anticipation = motion.anticipation_px
    * Math.sin(Math.PI * clamp(timeSeconds / Math.max(anticipationEnd, 1e-8), 0, 1));
  const rootX = origin.x - anticipation;
  const shoulder = {
    x: rootX + character.shoulder.offset_x,
    y: origin.y + character.shoulder.offset_y,
  };
  const restPose = character.rest_pose;
  const idleWrist = {
    x: origin.x + restPose.wrist_offset_x - anticipation * 0.2,
    y: origin.y + restPose.wrist_offset_y,
  };
  const finalWrist = {
    x: board.target_x - character.hand_length,
    y: board.target_y,
  };
  const reachProgress = smoothstep((timeSeconds - anticipationEnd) / motion.reach_seconds);

  let desiredWrist = {
    x: lerp(idleWrist.x, finalWrist.x, reachProgress),
    y: lerp(idleWrist.y, finalWrist.y, reachProgress),
  };
  let settleAmplitudeUsedPx = 0;
  if (timeSeconds > reachEnd) {
    const settleTime = timeSeconds - reachEnd;
    const decay = Math.exp(-motion.settle_decay * settleTime);
    const maxSafeReach = character.upper_arm_length + character.forearm_length - 0.05;
    const targetHeadroom = maxSafeReach - distance(shoulder, finalWrist);
    settleAmplitudeUsedPx = Math.min(
      motion.settle_amplitude_px,
      Math.max(0, targetHeadroom / 1.1),
    );
    desiredWrist = {
      x: desiredWrist.x
        + settleAmplitudeUsedPx * decay * Math.sin(motion.settle_frequency * settleTime),
      y: desiredWrist.y
        + settleAmplitudeUsedPx * 0.25 * decay * Math.cos(motion.settle_frequency * settleTime),
    };
  }

  const ik = solveTwoBoneIK(
    shoulder,
    desiredWrist,
    character.upper_arm_length,
    character.forearm_length,
    motion.elbow_bend,
  );

  // The hand was previously drawn at a fixed horizontal angle on every frame.
  // That created a visible wrist kink when the forearm was angled during anticipation.
  // Start aligned to the forearm and ease toward a straight pointing hand during reach.
  const forearmAngle = Math.atan2(
    ik.wrist.y - ik.elbow.y,
    ik.wrist.x - ik.elbow.x,
  );
  const handAngle = lerp(forearmAngle, 0, reachProgress);
  const fingerTip = {
    x: ik.wrist.x + Math.cos(handAngle) * character.hand_length,
    y: ik.wrist.y + Math.sin(handAngle) * character.hand_length,
  };

  const targetContactPoint = { x: board.target_x, y: board.target_y };
  const pelvis = { x: rootX + 4, y: origin.y + character.pelvis_y };

  return {
    frameIndex,
    timeSeconds,
    phase: timeSeconds < anticipationEnd
      ? "anticipate"
      : timeSeconds < reachEnd
        ? "reach"
        : timeSeconds < reachEnd + 0.7
          ? "settle"
          : "hold",
    root: { x: rootX, y: origin.y },
    head: {
      x: rootX + character.head.offset_x,
      y: origin.y + character.head.offset_y,
    },
    shoulder,
    elbow: ik.elbow,
    wrist: ik.wrist,
    requestedWrist: desiredWrist,
    fingerTip,
    handAngle,
    forearmAngle,
    pelvis,
    target: { x: board.target_x, y: board.target_y },
    diagnostics: {
      reachable: ik.reachable,
      requestedReachPx: ik.requestedDistance,
      maxReachPx: character.upper_arm_length + character.forearm_length,
      upperSegmentErrorPx: ik.upperError,
      lowerSegmentErrorPx: ik.lowerError,
      requestedTargetErrorPx: distance(ik.wrist, desiredWrist),
      targetErrorPx: distance(fingerTip, targetContactPoint),
      settleAmplitudeUsedPx,
    },
  };
}
