#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { renderSceneSvg } from "../src/svg-renderer.mjs";
import { evaluateRenderedPoseQuality } from "../src/rendered-pose-quality.mjs";

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const [sceneArg = "scenes/scene-001.json", outputArg = "out/rendered-pose-report.json"] = process.argv.slice(2);
const [scenePath, outputPath] = [sceneArg, outputArg].map(value => path.resolve(ROOT, value));

async function main() {
  const scene = JSON.parse(await fs.readFile(scenePath, "utf8"));
  const results = [];
  for (let frameIndex = 0; frameIndex < scene.duration_frames; frameIndex += 1) {
    const svg = renderSceneSvg(scene, frameIndex);
    results.push(evaluateRenderedPoseQuality(scene, frameIndex, svg));
  }
  const failed = results.filter(result => !result.passed);
  const report = {
    report_schema_version: "1.0.0",
    validation_id: "serialized-svg-rendered-pose-v1",
    evidence_class: "RENDERED_GEOMETRY_CONTRACT",
    source_scene: path.relative(ROOT, scenePath),
    rendered_frames_checked: results.length,
    passed_frames: results.length - failed.length,
    failed_frames: failed.length,
    status: failed.length ? "FAIL" : "PASS",
    thresholds: {
      max_rendered_aim_error_degrees: scene.quality_contract.max_hand_aim_error_degrees,
      max_rendered_hand_origin_error_px: 0.01,
      max_rendered_finger_tip_error_px: 0.05,
      max_rendered_hand_scale_error: 0.005
    },
    limitation: "This checks the emitted SVG transform against the deterministic pose state; it is not an aesthetic or human-motion acceptance score.",
    results
  };
  await fs.mkdir(path.dirname(outputPath), { recursive: true });
  await fs.writeFile(outputPath, JSON.stringify(report, null, 2) + "\n", "utf8");
  console.log(JSON.stringify({
    validation_id: report.validation_id,
    status: report.status,
    rendered_frames_checked: report.rendered_frames_checked,
    passed_frames: report.passed_frames,
    failed_frames: report.failed_frames,
    output: path.relative(ROOT, outputPath),
    failures: failed.slice(0, 12)
  }, null, 2));
  if (failed.length) process.exitCode = 1;
}
main().catch(error => {
  console.error(error?.stack || String(error));
  process.exitCode = 1;
});
