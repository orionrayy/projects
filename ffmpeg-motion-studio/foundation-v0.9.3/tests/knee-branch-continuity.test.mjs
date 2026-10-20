import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { evaluateLocomotion } from '../src/locomotion.mjs';

const scenes = [
  ['carry', JSON.parse(fs.readFileSync(new URL('../scenes/locomotion-lab.json', import.meta.url), 'utf8'))],
  ['free', JSON.parse(fs.readFileSync(new URL('../scenes/locomotion-free.json', import.meta.url), 'utf8'))]
];

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
    let previous = null;
    let previousStep = null;
    for (let frame = 0; frame < scene.duration_frames; frame++) {
      const pose = evaluateLocomotion(scene, frame, mode);
      const knees = [pose.leftLeg.knee, pose.rightLeg.knee];
      if (previous) {
        let step = 0;
        for (let side = 0; side < 2; side++) {
          step = Math.max(step, Math.hypot(knees[side].x - previous[side].x, knees[side].y - previous[side].y));
        }
        maxKneeStep = Math.max(maxKneeStep, step);
        if (previousStep !== null) maxKneeAcceleration = Math.max(maxKneeAcceleration, Math.abs(step - previousStep));
        previousStep = step;
      }
      previous = knees;
    }
    assert.ok(maxKneeStep < 13, mode + ' knee step spike: ' + maxKneeStep);
    assert.ok(Number.isFinite(maxKneeAcceleration), mode + ' knee acceleration must be finite');
    assert.ok(maxKneeAcceleration < Math.max(8, scene.motion.stride_length_px * (scene.motion.screen_stride_scale || 1) * 0.12),
      mode + ' knee acceleration spike: ' + maxKneeAcceleration);
  }
});
