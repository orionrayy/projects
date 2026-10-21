import test from "node:test";
import assert from "node:assert/strict";
import { keyCurve } from "../src/activity-motion.mjs";

const keys = [[0, 0], [0.2, 10], [0.4, 10], [0.6, -4], [0.8, -4], [1, 0]];
const curve = x => keyCurve(x, keys);
const h = 1e-5;

test("activity curves enter and leave the clip at rest with bounded endpoint acceleration", () => {
  const startVelocity = (curve(h) - curve(0)) / h;
  const endVelocity = (curve(1) - curve(1 - h)) / h;
  const startAcceleration = (curve(2*h) - 2*curve(h) + curve(0)) / (h*h);
  const endAcceleration = (curve(1) - 2*curve(1-h) + curve(1-2*h)) / (h*h);

  assert.ok(Math.abs(startVelocity) < 0.01, "start velocity should be zero: " + startVelocity);
  assert.ok(Math.abs(endVelocity) < 0.01, "end velocity should be zero: " + endVelocity);
  assert.ok(Math.abs(startAcceleration) < 2, "start acceleration should be bounded: " + startAcceleration);
  assert.ok(Math.abs(endAcceleration) < 2, "end acceleration should be bounded: " + endAcceleration);
});

test("internal action keys join with continuous acceleration", () => {
  for (const [x] of keys.slice(1, -1)) {
    const leftAcceleration = (curve(x) - 2*curve(x-h) + curve(x-2*h)) / (h*h);
    const rightAcceleration = (curve(x+2*h) - 2*curve(x+h) + curve(x)) / (h*h);
    const mismatch = Math.abs(leftAcceleration - rightAcceleration);
    assert.ok(mismatch < 2, "acceleration discontinuity at u=" + x + ": " + mismatch);
  }
});

test("quintic action curves preserve exact key values, range, and monotone segments", () => {
  for (const [x, y] of keys) assert.ok(Math.abs(curve(x) - y) < 1e-10, "key value changed at u=" + x);

  for (let i=0; i<keys.length-1; i++) {
    const [x0, y0] = keys[i], [x1, y1] = keys[i+1];
    let previous = curve(x0);
    for (let sample=1; sample<=100; sample++) {
      const x = x0 + (x1-x0)*sample/100;
      const value = curve(x);
      assert.ok(value >= Math.min(y0,y1)-1e-8 && value <= Math.max(y0,y1)+1e-8,
        "curve overshot segment range between " + x0 + " and " + x1);
      if (y1 > y0) assert.ok(value >= previous-1e-8, "increasing segment reversed direction at u=" + x);
      if (y1 < y0) assert.ok(value <= previous+1e-8, "decreasing segment reversed direction at u=" + x);
      if (y1 === y0) assert.ok(Math.abs(value-y0) < 1e-8, "flat hold drifted at u=" + x);
      previous = value;
    }
  }
});
