import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { distance, evaluateFrame } from "../src/motion-core.mjs";
import { renderSceneSvg } from "../src/svg-renderer.mjs";

const scene = JSON.parse(
  fs.readFileSync(new URL("../scenes/scene-001.json", import.meta.url), "utf8"),
);

test("rendered character includes a connected neck and visible shoulder/upper-arm layer", () => {
  const svg = renderSceneSvg(scene, 0);
  assert.match(svg, /id="neck"/);
  assert.match(svg, /id="torso"/);
  assert.match(svg, /id="upper-arm"/);
  assert.match(svg, /id="upper-arm"[\s\S]*?stroke-width="2.5"/);
});

test("hand starts aligned to the forearm and eases to a straight contact pose", () => {
  const start = evaluateFrame(scene, 0);
  const expectedForearmAngle = Math.atan2(
    start.wrist.y - start.elbow.y,
    start.wrist.x - start.elbow.x,
  );
  assert.ok(Math.abs(start.handAngle - expectedForearmAngle) < 1e-10);

  const end = evaluateFrame(scene, scene.duration_frames - 1);
  assert.ok(Math.abs(end.handAngle) < 1e-10);
  assert.ok(distance(end.fingerTip, { x: scene.board.target_x, y: scene.board.target_y }) < 0.02);
  assert.ok(Math.abs(distance(end.wrist, end.fingerTip) - scene.character.hand_length) < 0.1);
});

test("target state label does not claim contact while the hand is still approaching", () => {
  const startSvg = renderSceneSvg(scene, 0);
  const reachSvg = renderSceneSvg(scene, 22);
  const holdSvg = renderSceneSvg(scene, 65);
  assert.match(startSvg, /TARGET AHEAD/);
  assert.match(reachSvg, /TARGET AHEAD/);
  assert.match(holdSvg, /TARGET CONTACT/);
});

test("all frames preserve finite articulated geometry and a fixed two-link rig", () => {
  for (let frame = 0; frame < scene.duration_frames; frame += 1) {
    const state = evaluateFrame(scene, frame);
    for (const point of [
      state.shoulder, state.elbow, state.wrist, state.fingerTip,
    ]) {
      assert.ok(Number.isFinite(point.x), "finite x at frame " + frame);
      assert.ok(Number.isFinite(point.y), "finite y at frame " + frame);
    }
    assert.ok(state.diagnostics.upperSegmentErrorPx < 0.02, "upper segment at frame " + frame);
    assert.ok(state.diagnostics.lowerSegmentErrorPx < 0.02, "lower segment at frame " + frame);
    assert.ok(Math.abs(distance(state.wrist, state.fingerTip) - scene.character.hand_length) < 0.1,
      "hand length at frame " + frame);
  }
});

test("anticipation keeps the elbow in front of the torso instead of folding behind the shoulder", () => {
  const anticipationFrames = Math.floor(scene.motion.anticipation_seconds * scene.fps);
  for (let frame = 0; frame <= anticipationFrames; frame += 1) {
    const state = evaluateFrame(scene, frame);
    assert.ok(
      state.elbow.x > state.shoulder.x,
      "elbow should remain forward of shoulder at frame " + frame,
    );
    assert.ok(
      state.wrist.x > state.elbow.x,
      "wrist should remain forward of elbow at frame " + frame,
    );
  }
});

test("pointing hand has separate palm, index finger and thumb geometry", () => {
  for (const frame of [0, 15, 22, 36, 65, 95]) {
    const svg = renderSceneSvg(scene, frame);
    assert.match(svg, /id="pointing-hand"/);
    assert.match(svg, /id="index-finger"/);
    assert.match(svg, /id="palm"/);
    assert.match(svg, /id="thumb"/);
    assert.match(svg, /id="folded-fingers"/);
  }
});
