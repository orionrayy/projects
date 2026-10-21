import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { evaluateLocomotion, solveTwoBoneIK } from '../src/locomotion.mjs';

const scenes = [
  ['carry', JSON.parse(fs.readFileSync(new URL('../scenes/locomotion-lab.json', import.meta.url), 'utf8'))],
  ['free', JSON.parse(fs.readFileSync(new URL('../scenes/locomotion-free.json', import.meta.url), 'utf8'))]
];

test('near-extension IK uses a bounded reach envelope rather than a straight-chain singularity', () => {
  const pose = solveTwoBoneIK(
    { x: 0, y: 0 },
    { x: 0, y: 158 },
    78,
    80,
    { x: 10, y: 70, preferForward: true }
  );
  assert.ok(pose.solvedReachPx < 158, 'near-extension pose must retain a small bend margin');
  assert.ok(pose.jointAngleDegrees > 155 && pose.jointAngleDegrees < 175,
    'heel-strike extension should remain extended without reaching the singularity: ' + pose.jointAngleDegrees);
  assert.ok(pose.endpointClampErrorPx <= 3.01, 'near-singular target remains within the explicit 3px flex margin');
  let previous = 0;
  for (let raw = 152; raw <= 158; raw += 0.25) {
    const sample = solveTwoBoneIK({ x: 0, y: 0 }, { x: 0, y: raw }, 78, 80,
      { x: 10, y: 70, preferForward: true });
    assert.ok(sample.solvedReachPx <= raw + 1e-7,
      'reach curve must not overshoot its requested target at ' + raw + 'px');
    assert.ok(sample.solvedReachPx >= previous - 1e-7,
      'reach curve must be monotone at ' + raw + 'px');
    previous = sample.solvedReachPx;
  }
});

test('knee IK remains on the same oriented side of the hip-to-ankle axis for every frame', () => {
  for (const [mode, scene] of scenes) {
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateLocomotion(scene, frame, mode);
      for (const leg of [pose.leftLeg, pose.rightLeg]) {
        const dx = leg.ankle.x - leg.hip.x;
        const dy = leg.ankle.y - leg.hip.y;
        const theta = Math.atan2(dy, dx);
        const nx = Math.sin(theta);
        const ny = -Math.cos(theta);
        const score = (leg.knee.x - leg.hip.x) * nx + (leg.knee.y - leg.hip.y) * ny;
        assert.ok(score > 0, JSON.stringify({ mode, frame, score, knee: leg.knee, hip: leg.hip, ankle: leg.ankle }));
      }
    }
  }
});

test('knee displacement stays bounded without weakening the existing temporal gate', () => {
  for (const [mode, scene] of scenes) {
    let maxKneeStep = 0;
    let maxKneeAcceleration = 0;
    let maxKneeStepDetail = null;
    let previous = null;
    let previousPrevious = null;
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateLocomotion(scene, frame, mode);
      const knees = [pose.leftLeg.knee, pose.rightLeg.knee];
      if (previous) {
        for (let side = 0; side < 2; side++) {
          const step = Math.hypot(knees[side].x - previous[side].x, knees[side].y - previous[side].y);
          if (step > maxKneeStep) {
            maxKneeStep = step;
            maxKneeStepDetail = { frame, side: side === 0 ? 'left' : 'right', step, current: knees[side], previous: previous[side],
              footPhase: side === 0 ? pose.leftFoot.phase : pose.rightFoot.phase,
              footStance: side === 0 ? pose.leftFoot.inStance : pose.rightFoot.inStance };
          }
          if (previousPrevious) {
            const before = previousPrevious[side], now = knees[side], prior = previous[side];
            const ax = now.x - 2 * prior.x + before.x;
            const ay = now.y - 2 * prior.y + before.y;
            maxKneeAcceleration = Math.max(maxKneeAcceleration, Math.hypot(ax, ay));
          }
        }
      }
      previousPrevious = previous;
      previous = knees;
    }
    assert.ok(maxKneeStep < 13, mode + ' knee step spike: ' + JSON.stringify(maxKneeStepDetail));
    assert.ok(Number.isFinite(maxKneeAcceleration), mode + ' knee acceleration must be finite');
    assert.ok(maxKneeAcceleration < Math.max(8, scene.motion.stride_length_px * (scene.motion.screen_stride_scale || 1) * 0.12),
      mode + ' knee acceleration spike: ' + maxKneeAcceleration);
  }
});
