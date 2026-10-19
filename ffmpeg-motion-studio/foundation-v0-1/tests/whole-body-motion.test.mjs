import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { evaluateFrame } from "../src/motion-core.mjs";
import { evaluateWholeBodyMotion, phaseFromTravel } from "../src/whole-body-motion.mjs";

const near = (a, b, eps = 1e-9) => assert.ok(Math.abs(a - b) < eps, `${a} !~= ${b}`);

test("whole-body motion is deterministic and periodic", () => {
  for (const phase of [0, 0.2, Math.PI / 2, Math.PI, 4.9, 2 * Math.PI]) {
    const a = evaluateWholeBodyMotion({ phase, carryWeight: 0.75 });
    assert.deepEqual(a, evaluateWholeBodyMotion({ phase, carryWeight: 0.75 }));
    const b = evaluateWholeBodyMotion({ phase: phase + 2 * Math.PI, carryWeight: 0.75 });
    near(a.pelvis.bounceY, b.pelvis.bounceY);
    near(a.torso.pitch, b.torso.pitch);
    near(a.carriedProp.offsetX, b.carriedProp.offsetX);
  }
});

test("travel distance maps deterministically to gait phase", () => {
  near(phaseFromTravel(0, 108), 0);
  near(phaseFromTravel(108, 108), 2 * Math.PI);
  near(phaseFromTravel(54, 108), Math.PI);
  assert.throws(() => phaseFromTravel(1, 0), RangeError);
});

test("carrying locks arm swing and activates prop response", () => {
  const free = evaluateWholeBodyMotion({ phase: 1.2, carryWeight: 0 });
  const carry = evaluateWholeBodyMotion({ phase: 1.2, carryWeight: 1 });
  assert.notEqual(free.arms.leftSwing, 0);
  near(carry.arms.leftSwing, 0);
  near(carry.arms.rightSwing, 0);
  assert.notEqual(carry.arms.elbowResponse, 0);
  assert.notEqual(carry.carriedProp.offsetX, 0);
  assert.notEqual(carry.carriedProp.rotation, 0);
});

test("head and torso counter-motion remain bounded and phase-coupled", () => {
  const values = Array.from({ length: 240 }, (_, i) => evaluateWholeBodyMotion({ phase: 2 * Math.PI * i / 240, carryWeight: 1 }));
  assert.ok(Math.max(...values.map(v => v.torso.pitch)) < 0.08);
  assert.ok(Math.min(...values.map(v => v.torso.pitch)) > -0.05);
  assert.ok(Math.max(...values.map(v => Math.abs(v.head.counterSwayX))) < 2);
  assert.ok(Math.max(...values.map(v => Math.abs(v.carriedProp.rotation))) < 0.05);
  assert.ok(values.some(v => Math.abs(v.torso.shoulderSwayX) > 1));
});

test("motion-core exposes whole-body channels only when scene opts in", () => {
  const source = JSON.parse(fs.readFileSync(new URL("../scenes/scene-001.json", import.meta.url), "utf8"));
  assert.equal(evaluateFrame(source, 20).wholeBodyMotion, null);
  const scene = structuredClone(source);
  scene.motion.whole_body_motion = { enabled: true, cycles_per_second: 1, carry_weight: 1, scale: 1.5, facing: 1 };
  const a = evaluateFrame(scene, 7), b = evaluateFrame(scene, 7), c = evaluateFrame(scene, 19);
  assert.deepEqual(a.wholeBodyMotion, b.wholeBodyMotion);
  assert.notDeepEqual(a.wholeBodyMotion, c.wholeBodyMotion);
  assert.equal(a.wholeBodyMotion.carriedProp.weight, 1);
});
