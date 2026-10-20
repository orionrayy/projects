import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {renderSvgFrame,summarizeScene} from "../scripts/render-preview.mjs";

const carry=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json",import.meta.url),"utf8"));
const free=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json",import.meta.url),"utf8"));

test("limbs use continuous organic contours and integrated joints",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const svg=renderSvgFrame(scene,96,mode);
    const organic=(svg.match(/data-contour="organic"/g)||[]).length;
    assert.ok(organic>=8,"all limb segments should use organic contours: "+organic);
    assert.equal((svg.match(/data-anatomy="knee-fold"/g)||[]).length,2,"both knees need subtle integrated fold detail");
    assert.equal((svg.match(/data-anatomy="elbow-fold"/g)||[]).length,2,"both elbows need subtle integrated fold detail");
    assert.equal((svg.match(/data-anatomy="sleeve-cuff"/g)||[]).length,2,"sleeve ends should read as clothing rather than bare sticks");
    assert.equal((svg.match(/data-anatomy="hand"/g)||[]).length,2,"both hands must render");
    assert.equal((svg.match(/data-anatomy="finger-detail"/g)||[]).length,2,"both hands must show finger articulation cues");
  }
});

test("carry hands show grip detail and free-arm hands stay relaxed",()=>{
  const carrySvg=renderSvgFrame(carry,64,"carry"),freeSvg=renderSvgFrame(free,64,"free");
  assert.equal((carrySvg.match(/data-grip="grip"/g)||[]).length,2);
  assert.equal((freeSvg.match(/data-grip="relaxed"/g)||[]).length,2);
  assert.match(carrySvg,/data-anatomy="palm"/);
  assert.match(carrySvg,/data-anatomy="thumb-fold"/);
  assert.match(freeSvg,/MOTION STUDIO \/ v0\.9\.3/);
});

test("organic contours preserve contact, proportion, deterministic and temporal gates",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const r=summarizeScene(scene,mode),t=r.temporalDiagnostics;
    assert.equal(r.sceneVersion,"0.9.3");
    assert.ok(r.maxBoneLengthErrorPx<0.02);
    assert.ok(r.maxGroundPenetrationPx<0.02);
    assert.ok(r.maxBasketContactErrorPx<0.02);
    assert.ok(t.maxJointAccelerationPxPerFrame2<8);
    assert.equal(r.humanVisualAcceptance,"pending");
    assert.equal(r.pixelLevelNaturalnessMeasurement,"not_performed");
  }
  const a=renderSvgFrame(carry,64,"carry");
  assert.equal(a,renderSvgFrame(carry,64,"carry"));
});
