import { evaluateWholeBodyMotion } from "./whole-body-motion.mjs";
import { evaluateAction } from "./action-model.mjs";
import { evaluatePoseQuality } from "./pose-quality.mjs";

export function clamp(value, low, high) {
  return Math.min(high, Math.max(low, value));
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
function candidate(shoulder, angle, length) {
  return {
    x: shoulder.x + length * Math.cos(angle),
    y: shoulder.y + length * Math.sin(angle),
  };
}

export function solveTwoBoneIK(shoulder, requestedWrist, upperLength, lowerLength, bend = 1, poleTarget = null) {
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
  const elbowOffset = Math.acos(cosine);
  const candidateA = candidate(shoulder, targetAngle + elbowOffset, upperLength);
  const candidateB = candidate(shoulder, targetAngle - elbowOffset, upperLength);
  const elbow = poleTarget
    ? distance(candidateA, poleTarget) <= distance(candidateB, poleTarget) ? candidateA : candidateB
    : bend >= 0 ? candidateA : candidateB;

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

  const action = evaluateAction(scene, frameIndex);
  const character = scene.character;
  // Optional locomotion channels remain inert unless a scene explicitly opts in.
  const locomotionConfig = scene.motion.whole_body_motion;
  const wholeBodyMotion = locomotionConfig?.enabled
    ? evaluateWholeBodyMotion({
      phase: 2 * Math.PI * action.timeSeconds * (locomotionConfig.cycles_per_second ?? 1),
      scale: locomotionConfig.scale ?? 1,
      facing: locomotionConfig.facing ?? 1,
      carryWeight: locomotionConfig.carry_weight ?? 0,
    })
    : null;
  const rightIK = solveTwoBoneIK(
    action.rig.screenRightShoulder,
    action.requestedWrist,
    character.upper_arm_length,
    character.forearm_length,
    scene.motion.elbow_bend,
    action.elbowPole,
  );
  const far = character.far_arm;
  const leftIK = solveTwoBoneIK(
    action.screenLeftShoulder,
    action.screenLeftWrist,
    far.upper_arm_length,
    far.forearm_length,
    far.elbow_bend,
    action.screenLeftElbowPole,
  );

  const handAngle = Math.atan2(
    action.target.y - rightIK.wrist.y,
    action.target.x - rightIK.wrist.x,
  );
  const fingerTip = {
    x: rightIK.wrist.x + Math.cos(handAngle) * character.hand_length,
    y: rightIK.wrist.y + Math.sin(handAngle) * character.hand_length,
  };
  const farHandAngle = Math.atan2(
    leftIK.wrist.y - leftIK.elbow.y,
    leftIK.wrist.x - leftIK.elbow.x,
  );
  const farHandTip = {
    x: leftIK.wrist.x + Math.cos(farHandAngle) * far.hand_length,
    y: leftIK.wrist.y + Math.sin(farHandAngle) * far.hand_length,
  };

  const diagnostics = {
    reachable: rightIK.reachable,
    requestedReachPx: rightIK.requestedDistance,
    maxReachPx: character.upper_arm_length + character.forearm_length,
    upperSegmentErrorPx: rightIK.upperError,
    lowerSegmentErrorPx: rightIK.lowerError,
    leftUpperSegmentErrorPx: leftIK.upperError,
    leftLowerSegmentErrorPx: leftIK.lowerError,
    leftArmReachable: leftIK.reachable,
    requestedTargetErrorPx: distance(rightIK.wrist, action.requestedWrist),
    targetErrorPx: distance(fingerTip, action.target),
    settleAmplitudeUsedPx: action.settleAmplitudeUsedPx,
  };

  const state = {
    frameIndex,
    timeSeconds: action.timeSeconds,
    phase: action.phase,
    wholeBodyMotion,
    root: action.rig.root,
    head: action.rig.head,
    headAngle: action.rig.headAngle,
    torsoAngle: action.rig.torsoAngle,
    neckBase: action.rig.neckBase,
    neckTop: action.rig.neckTop,
    pelvis: action.rig.pelvis,
    // Legacy aliases retained for preview controls; the scene contract is screen-sided.
    shoulder: rightIK.shoulder,
    elbow: rightIK.elbow,
    wrist: rightIK.wrist,
    requestedWrist: action.requestedWrist,
    fingerTip,
    handAngle,
    forearmAngle: Math.atan2(rightIK.wrist.y - rightIK.elbow.y, rightIK.wrist.x - rightIK.elbow.x),
    screenLeftArm: {
      shoulder: leftIK.shoulder,
      elbow: leftIK.elbow,
      wrist: leftIK.wrist,
      handTip: farHandTip,
      handAngle: farHandAngle,
      reachable: leftIK.reachable,
    },
    screenRightArm: {
      shoulder: rightIK.shoulder,
      elbow: rightIK.elbow,
      wrist: rightIK.wrist,
      handTip: fingerTip,
      handAngle,
      reachable: rightIK.reachable,
    },
    target: action.target,
    diagnostics,
    action: {
      reachProgress: action.reachProgress,
      anticipationWeight: action.anticipationWeight,
      settleTime: action.settleTime,
      holdTime: action.holdTime,
      contactWrist: action.contactWrist,
      restWrist: action.restWrist,
      elbowPole: action.elbowPole,
      screenLeftElbowPole: action.screenLeftElbowPole,
    },
  };
  state.quality = evaluatePoseQuality(scene, state);
  // Rendered hand aim is checked from serialized SVG in rendered-pose-quality.mjs.
  diagnostics.poseQualityPassed = state.quality.passed;
  return state;
}
