import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {distance,evaluateFrame} from "../src/motion-core.mjs";
import {renderSceneSvg} from "../src/svg-renderer.mjs";
import {evaluateRenderedPoseQuality} from "../src/rendered-pose-quality.mjs";
const scene=JSON.parse(fs.readFileSync(new URL("../scenes/scene-001.json",import.meta.url),"utf8"));
test("character SVG exposes rig and semantic hand groups",()=>{
 const svg=renderSceneSvg(scene,0);
 for(const id of ["neck","torso","upper-arm","pointing-hand","index-finger","palm","thumb","screen-left-arm","screen-left-hand","screen-right-arm","legs"])assert.match(svg,new RegExp('id="'+id+'"'));
 assert.match(svg,/transform="rotate\(/);
});
test("index axis aims at target and terminal contact is exact",()=>{
 const start=evaluateFrame(scene,0),end=evaluateFrame(scene,scene.duration_frames-1);
 assert.ok(evaluateRenderedPoseQuality(scene,0,renderSceneSvg(scene,0)).passed);
 assert.ok(Math.abs(end.fingerTip.x-scene.board.target_x)<.1);
 assert.ok(Math.abs(end.fingerTip.y-scene.board.target_y)<.1);
 assert.ok(Math.abs(distance(end.wrist,end.fingerTip)-scene.character.hand_length)<.1);
});
test("target caption follows measured proximity",()=>{
 assert.match(renderSceneSvg(scene,0),/TARGET AHEAD/);
 assert.match(renderSceneSvg(scene,19),/TARGET AHEAD/);
 assert.match(renderSceneSvg(scene,92),/TARGET CONTACT/);
});
test("all frames preserve finite rig geometry, bone lengths and pose quality",()=>{
 for(let frame=0;frame<scene.duration_frames;frame++){
  const s=evaluateFrame(scene,frame);
  for(const p of [s.shoulder,s.elbow,s.wrist,s.fingerTip,s.head]){assert.ok(Number.isFinite(p.x));assert.ok(Number.isFinite(p.y));}
  assert.ok(s.diagnostics.upperSegmentErrorPx<scene.quality_contract.max_ik_segment_error_px);
  assert.ok(s.diagnostics.lowerSegmentErrorPx<scene.quality_contract.max_ik_segment_error_px);
  assert.ok(s.quality.passed,"frame "+frame+": "+s.quality.issues.join(","));
 }
});
test("anticipation is visible and returns to rest before reach",()=>{
 const first=evaluateFrame(scene,0),prep=evaluateFrame(scene,6),startReach=evaluateFrame(scene,12);
 assert.ok(distance(first.wrist,prep.wrist)>3);
 assert.ok(distance(first.wrist,startReach.wrist)<1.5);
});

test("bilateral rig exists in both data and rendered SVG",()=>{
 const svg=renderSceneSvg(scene,0);
 for(const id of scene.quality_contract.required_render_groups){
  assert.match(svg,new RegExp('id="'+id+'"'),"missing rendered group: "+id);
 }
 for(let frame=0;frame<scene.duration_frames;frame++){
  const s=evaluateFrame(scene,frame);
  assert.ok(s.screenLeftArm,"screen-left arm state at frame "+frame);
  assert.ok(s.screenRightArm,"screen-right arm state at frame "+frame);
  assert.ok(s.diagnostics.leftArmReachable,"screen-left arm reachability at frame "+frame);
  assert.ok(s.diagnostics.leftUpperSegmentErrorPx<scene.quality_contract.max_ik_segment_error_px);
  assert.ok(s.diagnostics.leftLowerSegmentErrorPx<scene.quality_contract.max_ik_segment_error_px);
 }
});
test("head center is aligned over the pelvis/root axis at neutral frame",()=>{
 const s=evaluateFrame(scene,0);
 assert.ok(Math.abs(s.head.x-s.root.x)<=3,"head centerline drift: "+Math.abs(s.head.x-s.root.x));
 assert.ok(Math.abs(s.pelvis.x-s.root.x)<=1);
});

test("serialized SVG hand aim, origin, tip and scale satisfy contract across every frame",()=>{
 for(let frame=0;frame<scene.duration_frames;frame++){
  const report=evaluateRenderedPoseQuality(scene,frame,renderSceneSvg(scene,frame));
  assert.ok(report.passed,"frame "+frame+": "+report.issues.join(", "));
 }
});
test("rendered-pose gate rejects an altered SVG hand rotation",()=>{
 const original=renderSceneSvg(scene,48);
 const corrupted=original.replace(
  /(id="pointing-hand" transform="translate\(-?[\d.]+ -?[\d.]+\) rotate\()(-?[\d.]+)/,
  (_,prefix,angle)=>prefix+String(Number(angle)+20)
 );
 assert.notEqual(corrupted,original,"mutation must alter the serialized transform");
 const report=evaluateRenderedPoseQuality(scene,48,corrupted);
 assert.equal(report.passed,false);
 assert.ok(report.issues.includes("RENDERED_HAND_AIM"));
 assert.ok(report.issues.includes("RENDERED_FINGER_TIP"));
});
test("rendered-pose gate fails closed when index-finger geometry is missing",()=>{
 const svg=renderSceneSvg(scene,24).replace(/<g id="index-finger">[\s\S]*?<\/g>/,"");
 const report=evaluateRenderedPoseQuality(scene,24,svg);
 assert.equal(report.passed,false);
 assert.ok(report.issues.includes("INDEX_FINGER_GROUP_MISSING"));
});
