import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {distance,evaluateFrame} from "../src/motion-core.mjs";
const scene=JSON.parse(fs.readFileSync(new URL("../scenes/scene-001.json",import.meta.url),"utf8"));
test("hand orientation remains aimed at target across the full timeline",()=>{
 for(let f=0;f<scene.duration_frames;f++){const s=evaluateFrame(scene,f);assert.ok(s.quality.handAimErrorDegrees<=scene.quality_contract.max_hand_aim_error_degrees,"frame "+f);}
});
test("contact remains within contract during hold",()=>{
 for(let f=0;f<scene.duration_frames;f++){const s=evaluateFrame(scene,f);if(s.phase==="hold")assert.ok(distance(s.fingerTip,s.target)<=scene.quality_contract.max_hold_target_error_px,"frame "+f);}
});
test("wrist path visibly arcs during reach",()=>{
 const p0=evaluateFrame(scene,12),pm=evaluateFrame(scene,22),p1=evaluateFrame(scene,32);
 assert.ok(Math.abs(pm.wrist.y-(p0.wrist.y+p1.wrist.y)/2)>=4);
});
test("torso and head respond instead of remaining rigid",()=>{
 const poses=Array.from({length:scene.duration_frames},(_,f)=>evaluateFrame(scene,f));
 assert.ok(Math.max(...poses.map(s=>Math.abs(s.torsoAngle)))>=.035);
 assert.ok(Math.max(...poses.filter(s=>s.phase==="hold").map(s=>Math.abs(s.torsoAngle)))<.025);
 assert.ok(poses.some((s,i)=>i>0&&Math.abs(s.headAngle-poses[i-1].headAngle)>.0001));
});
test("all poses retain exact bone lengths and deterministic random access",()=>{
 for(const f of [70,0,95,16,38])assert.deepEqual(evaluateFrame(scene,f),evaluateFrame(scene,f));
 for(let f=0;f<scene.duration_frames;f++){const s=evaluateFrame(scene,f);assert.ok(s.diagnostics.upperSegmentErrorPx<.02);assert.ok(s.diagnostics.lowerSegmentErrorPx<.02);}
});
