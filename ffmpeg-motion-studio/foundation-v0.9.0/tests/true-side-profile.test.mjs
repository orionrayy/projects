import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {renderSvgFrame} from "../scripts/render-preview.mjs";

const carry=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json",import.meta.url),"utf8"));
const free=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json",import.meta.url),"utf8"));

test("renderer is explicitly side-profile rather than frontal",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const svg=renderSvgFrame(scene,48,mode);
    assert.match(svg,/data-view="profile-right"/);
    assert.equal((svg.match(/data-profile-feature="eye"/g)||[]).length,1,"profile head must show one visible eye");
    for(const feature of ["nose","ear","mouth"]) assert.ok(svg.includes('data-profile-feature="'+feature+'"'),"missing profile feature "+feature);
    assert.ok((svg.match(/data-contour="side-profile"/g)||[]).length>=2,"head and torso must both be profiled");
    assert.equal((svg.match(/data-leg-depth="near"/g)||[]).length,1);
    assert.equal((svg.match(/data-leg-depth="far"/g)||[]).length,1);
    assert.ok(scene.character.far_thigh_width_px<scene.character.thigh_width_px);
    assert.ok(scene.character.far_knee_width_px<scene.character.knee_width_px);
    assert.ok(scene.character.shoulder_depth_projection_px<=6);
  }
});

test("far-side leg is narrower and rendered before the near-side leg",()=>{
  const svg=renderSvgFrame(carry,48,"carry");
  const farStart=svg.indexOf('data-leg-depth="far"'),nearStart=svg.indexOf('data-leg-depth="near"');
  assert.ok(farStart>=0&&nearStart>farStart,"far leg should draw first behind near leg");
  assert.ok((svg.match(/data-contour="organic"/g)||[]).length>=8);
});
