import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {renderSvgFrame, summarizeScene} from "../scripts/render-preview.mjs";

const carry = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"));
const free = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));

test("SVG preview is deterministic and visibly applies head counter-rotation", () => {
  const svg = renderSvgFrame(carry, 64, "carry");
  assert.equal(svg, renderSvgFrame(carry, 64, "carry"));
  assert.match(svg, /<svg .*width="1280" height="720"/);
  assert.match(svg, /Carry interaction/);
  const poseSummary = summarizeScene(carry, "carry");
  assert.ok(poseSummary.headAngleRangeDegrees > 0.1);
  assert.ok(poseSummary.headAngleRangeDegrees < 15);
  assert.match(svg, /transform="rotate\(/);
});

test("carry and free-arm profiles produce distinct reviewable frames", () => {
  const carrySvg = renderSvgFrame(carry, 48, "carry");
  const freeSvg = renderSvgFrame(free, 48, "free");
  assert.notEqual(carrySvg, freeSvg);
  assert.match(carrySvg, /Carry interaction/);
  assert.match(freeSvg, /Free-arm counter-swing/);
});

test("complete preview preflight distinguishes geometry from artistic review", () => {
  for (const [scene, mode] of [[carry, "carry"], [free, "free"]]) {
    const report = summarizeScene(scene, mode);
    assert.equal(report.frameCount, 192);
    assert.equal(report.fps, 24);
    assert.equal(report.durationSeconds, 8);
    assert.equal(report.allPoseValuesFinite, true);
    assert.ok(report.maxBoneLengthErrorPx <= 0.02);
    assert.ok(report.maxGroundPenetrationPx <= 0.02);
    assert.ok(report.minProjectedFootSeparationPx >= 30, "projected feet need a readable separation margin");
    assert.ok(report.torsoAngleRangeDegrees >= 8, "torso response must be visible across a gait cycle");
    assert.ok(report.headAngleRangeDegrees >= 5, "head response must be visible across a gait cycle");
    if (mode === "free") assert.ok(report.nearArmWristRelativeRangePx >= 50, "free arm must visibly counter-swing");
    if (mode === "carry") assert.ok(report.maxBasketContactErrorPx <= 0.02);
    assert.equal(report.humanVisualAcceptance, "pending");
    assert.equal(report.pixelLevelNaturalnessMeasurement, "not_performed");
    assert.equal(report.browserFfmpegRasterParity, "not_verified");
  }
});

test("renderer rejects invalid arm modes and out-of-range frames", () => {
  assert.throws(() => renderSvgFrame(carry, -1, "carry"), RangeError);
  assert.throws(() => renderSvgFrame(carry, carry.duration_frames, "carry"), RangeError);
  assert.throws(() => renderSvgFrame(carry, 0, "invalid"), RangeError);
});
