import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {measureKeyframeClip, outputFrameCount, sampleKeyframeClip, validateKeyframeClip} from "../src/keyframe-clip.mjs";
const source=JSON.parse(fs.readFileSync(new URL("../reference-data/stickman-step/clip.json",import.meta.url),"utf8"));
function makeRigClip(count){
 const clip=structuredClone(source), names=Array.from({length:count},(_,i)=>"joint-"+i);
 clip.clip_id="synthetic-rig-"+count;
 clip.rig={landmark_order:names,point_id_by_landmark:Object.fromEntries(names.map((n,i)=>[n,i+1])),parent_by_landmark:Object.fromEntries(names.map((n,i)=>[n,i===0?null:names[i-1]])),root_landmark:names[0],head_landmark:names[count-1]};
 clip.quality_contract={max_parent_segment_length_variation_px:0.1,root_expected_horizontal_direction:"none",note:"Synthetic topology stress fixture; not a biological rig."};
 clip.keyframes=clip.keyframes.map(k=>({source_frame_id:k.source_frame_id,landmarks:Object.fromEntries(names.map((n,i)=>[n,{x:200+(i%200)*0.4,y:50+(i%180)*0.5}]))}));
 return clip;
}
test("synthetic rigs with 6, 27, 30, 64 and 128 landmarks remain valid",()=>{
 for(const n of [6,27,30,64,128]){
  const c=makeRigClip(n),v=validateKeyframeClip(c),m=measureKeyframeClip(c);
  assert.equal(v.valid,true,"validity for "+n);assert.equal(v.landmarkCount,n);assert.equal(m.parentSegmentCount,n-1);assert.equal(m.outputFrameCount,33);assert.equal(m.passed,true,JSON.stringify(m.checks));assert.deepEqual(sampleKeyframeClip(c,16),sampleKeyframeClip(c,16));
 }
});
test("parent graph depth 26 is handled without truncation",()=>{
 const c=makeRigClip(27),m=measureKeyframeClip(c);let depth=0,node=c.rig.head_landmark;
 while(c.rig.parent_by_landmark[node]!==null){node=c.rig.parent_by_landmark[node];depth++;}
 assert.equal(depth,26);assert.equal(m.parentSegmentCount,26);
});
test("duplicate point ids and mismatched ordered landmarks fail closed",()=>{
 const duplicate=makeRigClip(6);duplicate.rig.point_id_by_landmark["joint-1"]=1;assert.throws(()=>validateKeyframeClip(duplicate),/duplicate point ids/);
 const order=makeRigClip(6);order.rig.landmark_order.reverse();assert.throws(()=>validateKeyframeClip(order),/landmark_order must match/);
});
test("a non-null root parent fails closed",()=>{
 const c=makeRigClip(6);c.rig.parent_by_landmark["joint-0"]="joint-1";assert.throws(()=>validateKeyframeClip(c),/root landmark must not have a parent|parent cycle/);
});