import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {evaluateLocomotion} from "../src/locomotion.mjs";
import {renderSvgFrame,summarizeScene} from "../scripts/render-preview.mjs";
const carry=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json",import.meta.url),"utf8"));
const free=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json",import.meta.url),"utf8"));
test("anatomical proportions have a readable torso, compact neck and human-scale stature",()=>{
  for(const [s,m] of [[carry,"carry"],[free,"free"]]){
    const a=summarizeScene(s,m).anatomyDiagnostics;
    assert.ok(a.torsoToHeadRatio>=1.8&&a.torsoToHeadRatio<=2.4,"torso proportion");
    assert.ok(a.neckToHeadRatio>=0.2&&a.neckToHeadRatio<=0.62,"neck proportion");
    assert.ok(a.legToTorsoRatio>=1.6&&a.legToTorsoRatio<=2.15,"leg-to-torso proportion");
    assert.ok(a.statureInHeadUnits>=6.4&&a.statureInHeadUnits<=8.0,"stature proportion");
    assert.ok(a.hipHalfWidthPx<a.shoulderHalfWidthPx,"hips wider than shoulders");
  }
});
test("render includes shaped anatomy and articulated hands",()=>{
  const pose=evaluateLocomotion(carry,64,"carry"),svg=renderSvgFrame(carry,64,"carry");
  for(const m of ['data-anatomy="torso"','data-anatomy="neck"','data-anatomy="head"','data-anatomy="limb"','data-anatomy="knee"','data-anatomy="hand"','data-anatomy="shoe"']) assert.ok(svg.includes(m),"missing region "+m);
  assert.ok(Math.hypot(pose.chest.x-pose.pelvis.x,pose.chest.y-pose.pelvis.y)>90);
  assert.equal((svg.match(/data-anatomy="hand"/g)||[]).length,2);
  assert.match(svg,/data-grip="grip"/);
  assert.match(renderSvgFrame(free,64,"free"),/data-grip="relaxed"/);
});
test("anatomy remains deterministic and naturalness requires human acceptance",()=>{
  assert.equal(renderSvgFrame(carry,78,"carry"),renderSvgFrame(carry,78,"carry"));
  const r=summarizeScene(carry,"carry");
  assert.equal(r.humanVisualAcceptance,"pending");
  assert.equal(r.pixelLevelNaturalnessMeasurement,"not_performed");
  assert.ok(Number.isFinite(r.anatomyDiagnostics.neckLengthPx)&&r.anatomyDiagnostics.neckLengthPx>0);
});
