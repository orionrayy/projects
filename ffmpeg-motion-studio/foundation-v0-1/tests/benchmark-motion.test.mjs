import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {evaluateFrame,distance} from "../src/motion-core.mjs";
import {inspectSceneLayout} from "../src/layout-guards.mjs";
const root=new URL("../",import.meta.url);
const scene=JSON.parse(fs.readFileSync(new URL("scenes/scene-001.json",root),"utf8"));
const suite=JSON.parse(fs.readFileSync(new URL("benchmarks/motion-scenarios.json",root),"utf8"));
test("synthetic suite has unique cases and explicit endpoint expectations",()=>{
 const ids=suite.cases.map(item=>item.id);assert.equal(new Set(ids).size,ids.length);assert.ok(suite.cases.length>=7);
 assert.ok(suite.cases.every(item=>typeof item.expected_endpoint_reachable==="boolean"));
});
test("all synthetic scenarios preserve IK segment lengths through every frame",()=>{
 for(const x of suite.cases){const s=structuredClone(scene);s.board.target_x=x.target_x;s.board.target_y=x.target_y;s.character.upper_arm_length=x.upper_arm_length;s.character.forearm_length=x.forearm_length;
  for(let i=0;i<s.duration_frames;i++){const q=evaluateFrame(s,i);assert.ok(q.diagnostics.upperSegmentErrorPx<=suite.thresholds.max_segment_error_px,x.id+" upper "+i);assert.ok(q.diagnostics.lowerSegmentErrorPx<=suite.thresholds.max_segment_error_px,x.id+" lower "+i);}
 }
});
test("endpoint reachability matches the explicit scenario contract",()=>{
 for(const x of suite.cases){const s=structuredClone(scene);s.board.target_x=x.target_x;s.board.target_y=x.target_y;s.character.upper_arm_length=x.upper_arm_length;s.character.forearm_length=x.forearm_length;
  const q=evaluateFrame(s,s.duration_frames-1);assert.equal(q.diagnostics.reachable,x.expected_endpoint_reachable,x.id);
  if(x.expected_endpoint_reachable)assert.ok(distance(q.fingerTip,q.target)<=suite.thresholds.reachable_target_error_px,x.id);
 }
});
test("reachable target cases remain reachable throughout settling",()=>{
 for(const x of suite.cases.filter(item=>item.expected_endpoint_reachable)){const s=structuredClone(scene);s.board.target_x=x.target_x;s.board.target_y=x.target_y;s.character.upper_arm_length=x.upper_arm_length;s.character.forearm_length=x.forearm_length;
  for(let i=0;i<s.duration_frames;i++)assert.equal(evaluateFrame(s,i).diagnostics.reachable,true,x.id+" frame "+i);
 }
});
test("reachable target variants do not violate reserved layout zones",()=>{
 for(const x of suite.cases.filter(item=>item.expected_endpoint_reachable)){const s=structuredClone(scene);s.board.target_x=x.target_x;s.board.target_y=x.target_y;assert.deepEqual(inspectSceneLayout(s),[],x.id);}
});