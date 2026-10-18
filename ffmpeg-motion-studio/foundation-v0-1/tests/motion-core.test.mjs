import test from "node:test";import assert from "node:assert/strict";import fs from "node:fs";
import {evaluateFrame,solveTwoBoneIK,distance} from "../src/motion-core.mjs";import {renderSceneSvg} from "../src/svg-renderer.mjs";
const scene=JSON.parse(fs.readFileSync(new URL("../scenes/scene-001.json",import.meta.url),"utf8"));
test("same scene/frame returns identical state and SVG",()=>{for(const i of [0,1,12,24,32,48,72,95]){assert.deepEqual(evaluateFrame(scene,i),evaluateFrame(scene,i));assert.equal(renderSceneSvg(scene,i),renderSceneSvg(scene,i));}});
test("random access order does not mutate frame results",()=>{const frames=[0,24,48,72,95],expected=new Map(frames.map(i=>[i,evaluateFrame(scene,i)]));for(const i of [72,0,95,24,48])assert.deepEqual(evaluateFrame(scene,i),expected.get(i));});
test("reachable frames preserve IK segment lengths and hit target during hold",()=>{for(let i=0;i<scene.duration_frames;i++){const s=evaluateFrame(scene,i);assert.equal(s.diagnostics.reachable,true,"frame "+i);assert.ok(s.diagnostics.upperSegmentErrorPx<.02);assert.ok(s.diagnostics.lowerSegmentErrorPx<.02);if(s.phase==="hold")assert.ok(distance(s.fingerTip,s.target)<8,"target error at "+i);}});
test("unreachable IK is clamped and flagged instead of stretched",()=>{const x=solveTwoBoneIK({x:0,y:0},{x:1000,y:0},100,90,1);assert.equal(x.reachable,false);assert.ok(Math.abs(distance(x.shoulder,x.elbow)-100)<.02);assert.ok(Math.abs(distance(x.elbow,x.wrist)-90)<.02);});
test("invalid frame index fails closed",()=>{assert.throws(()=>evaluateFrame(scene,-1),RangeError);assert.throws(()=>evaluateFrame(scene,96),RangeError);assert.throws(()=>evaluateFrame(scene,1.5),TypeError);});
test("diagnostic overlay is opt-in and frame is labeled",()=>{const a=renderSceneSvg(scene,37),b=renderSceneSvg(scene,37,{showDiagnostics:true});assert.match(a,/frame 37/);assert.doesNotMatch(a,/id="diagnostics"/);assert.match(b,/id="diagnostics"/);});

test("bad scene cannot silently extend beyond declared timeline", () => {
  const mutated = { ...scene, duration_frames: 1 };
  assert.equal(evaluateFrame(mutated, 0).frameIndex, 0);
  assert.throws(() => evaluateFrame(mutated, 1), RangeError);
});
