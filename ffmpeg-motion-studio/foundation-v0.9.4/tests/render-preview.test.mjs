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
  const report = summarizeScene(carry, "carry");
  assert.ok(report.headAngleRangeDegrees > 0.1);
  assert.ok(report.headAngleRangeDegrees < 15);
  assert.match(svg, /transform="rotate\(/);
});

test("carry and free-arm profiles produce distinct reviewable frames", () => {
  const carrySvg = renderSvgFrame(carry, 48, "carry");
  const freeSvg = renderSvgFrame(free, 48, "free");
  assert.notEqual(carrySvg, freeSvg);
  assert.match(carrySvg, /#E9923A/);
  assert.doesNotMatch(freeSvg, /#E9923A|#B96D2A/, "free-arm mode must not show an unheld basket");
  assert.match(carrySvg, /Carry interaction/);
  assert.match(freeSvg, /Free-arm counter-swing/);
});

test("whole-sequence pose metrics preserve geometry and naturalness gates", () => {
  for (const [scene, mode] of [[carry,"carry"],[free,"free"]]) {
    const report = summarizeScene(scene, mode);
    assert.equal(report.frameCount, 192);
    assert.equal(report.fps, 24);
    assert.equal(report.durationSeconds, 8);
    assert.equal(report.allPoseValuesFinite, true);
    assert.ok(report.maxBoneLengthErrorPx <= 0.02);
    assert.ok(report.maxGroundPenetrationPx <= 0.02);
    assert.ok(report.minProjectedFootSeparationPx <= 30, "side-view feet should approach a narrow passing pose: " + report.minProjectedFootSeparationPx);
    assert.ok(report.torsoAngleRangeDegrees < 9);
    assert.ok(report.headAngleRangeDegrees < 6.5);
    if (mode === "carry") assert.ok(report.maxBasketContactErrorPx <= 0.02);
    if (mode === "carry") assert.ok(report.basketTiltRangeDegrees >= 0.5 && report.basketTiltRangeDegrees <= 3.0, "carry prop secondary tilt should remain subtle");
    if (mode === "free") {
      assert.ok(report.nearArmWristRelativeRangePx >= 18);
      assert.ok(report.minNearArmElbowAngleDegrees >= 110);
      assert.ok(report.maxNearArmElbowAngleDegrees <= 160);
    }
    assert.equal(report.humanVisualAcceptance,"pending");
    assert.equal(report.pixelLevelNaturalnessMeasurement,"not_performed");
    assert.equal(report.browserFfmpegRasterParity,"not_verified");
  }
});

test("renderer rejects invalid arm modes and out-of-range frames", () => {
  assert.throws(() => renderSvgFrame(carry,-1,"carry"), RangeError);
  assert.throws(() => renderSvgFrame(carry,carry.duration_frames,"carry"), RangeError);
  assert.throws(() => renderSvgFrame(carry,0,"invalid"), RangeError);
});
