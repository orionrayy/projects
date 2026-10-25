import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {evaluateLocomotion,footLocalOffset,sampleStanceWorldDrift,solveTwoBoneIK} from "../src/locomotion.mjs";
const carry=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json",import.meta.url),"utf8"));
const free=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json",import.meta.url),"utf8"));
const d=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
const range=a=>Math.max(...a)-Math.min(...a);

test("Hermite swing matches stance position and velocity at both boundaries",()=>{
 const s=carry.motion.stance_fraction,stride=carry.motion.stride_length_px,eps=1e-5;
 assert.ok(Math.abs(footLocalOffset(s-eps,stride,s)-footLocalOffset(s+eps,stride,s))<0.002);
 assert.ok(Math.abs((footLocalOffset(s,stride,s)-footLocalOffset(s-eps,stride,s))/eps+stride)<0.01);
 assert.ok(Math.abs((footLocalOffset(1,stride,s)-footLocalOffset(1-eps,stride,s))/eps+stride)<0.05);
});
test("pole-target IK preserves segment lengths and clamps unreachable targets",()=>{
 for(const target of [{x:25,y:40},{x:150,y:-5},{x:-80,y:70}]){
  const hip={x:0,y:0},pole={x:20,y:40},r=solveTwoBoneIK(hip,target,54,50,pole);
  assert.ok(Math.abs(d(hip,r.joint)-54)<1e-8);assert.ok(Math.abs(d(r.joint,r.end)-50)<1e-8);
 }
});
test("projected depth separation keeps bilateral legs from swapping order",()=>{
 for(let i=0;i<carry.duration_frames;i++){const s=evaluateLocomotion(carry,i,"carry");assert.ok(s.leftFoot.x-s.rightFoot.x>=8);assert.ok(s.leftHip.x>s.rightHip.x);assert.ok(s.leftLeg.knee.x>s.rightLeg.knee.x);}
});
test("every carry frame stays inside geometry and prop contact limits",()=>{
 for(let i=0;i<carry.duration_frames;i++){const s=evaluateLocomotion(carry,i,"carry");const a=carry.acceptance;
  assert.ok(s.diagnostics.boneLengthErrorPx<=a.max_bone_length_error_px);
  assert.ok(s.diagnostics.basketContactErrorPx<=a.max_basket_contact_error_px);
  assert.ok(s.diagnostics.groundPenetrationPx<=a.max_ground_penetration_px);
 }
});
test("free-arm profile has opposite-phase wrist counter-swing",()=>{
 const a=evaluateLocomotion(free,12,"free");
 const near=range(Array.from({length:free.duration_frames},(_,i)=>evaluateLocomotion(free,i,"free").nearArm.wrist.x-evaluateLocomotion(free,i,"free").rootX));
 const far=range(Array.from({length:free.duration_frames},(_,i)=>evaluateLocomotion(free,i,"free").farArm.wrist.x-evaluateLocomotion(free,i,"free").rootX));
 assert.ok(near>=20);assert.ok(far>=20);assert.equal(a.diagnostics.basketContactErrorPx,0);
});
test("carry hands keep separated handle contacts and visible elbow flexion",()=>{
 for(let i=0;i<carry.duration_frames;i++){const s=evaluateLocomotion(carry,i,"carry");
  assert.ok(d(s.nearArm.wrist,s.basket.handleRight)<1e-8);
  assert.ok(d(s.farArm.wrist,s.basket.handleLeft)<1e-8);
  assert.ok(s.nearArm.elbowAngleDegrees>=70&&s.nearArm.elbowAngleDegrees<=125);
  assert.ok(s.farArm.elbowAngleDegrees>=70&&s.farArm.elbowAngleDegrees<=125);
  assert.ok(s.basket.handleRight.x-s.basket.handleLeft.x>=30);
 }
});
test("stance feet remain anchored and frame sampling is deterministic",()=>{
 const order=[0,57,16,191,96,57];assert.deepEqual(evaluateLocomotion(carry,order[1]),evaluateLocomotion(carry,order[5]));
 for(let i=0;i<carry.duration_frames;i+=2){const s=evaluateLocomotion(carry,i);for(const side of ["left","right"]){if(!s[side+"Foot"].inStance)continue;
  assert.ok(sampleStanceWorldDrift(carry,i,side,9)<=carry.acceptance.max_stance_foot_drift_px);
 }}
});
test("joint and root displacements are bounded per frame",()=>{
 let elbow=0,knee=0,root=0;
 for(let i=1;i<carry.duration_frames;i++){const a=evaluateLocomotion(carry,i-1),b=evaluateLocomotion(carry,i);
  for(const k of ["nearArm","farArm"])elbow=Math.max(elbow,d(a[k].elbow,b[k].elbow));
  for(const k of ["leftLeg","rightLeg"])knee=Math.max(knee,d(a[k].knee,b[k].knee));
  root=Math.max(root,Math.abs(b.rootX-a.rootX));
 }
 assert.ok(elbow<=carry.acceptance.max_arm_elbow_step_px);assert.ok(knee<=carry.acceptance.max_knee_step_px);
 assert.ok(root<=carry.acceptance.max_root_step_px);
});
test("invalid frames and arm modes fail closed",()=>{
 assert.throws(()=>evaluateLocomotion(carry,-1),RangeError);
 assert.throws(()=>evaluateLocomotion(carry,carry.duration_frames),RangeError);
 assert.throws(()=>evaluateLocomotion(carry,0,"invalid"),RangeError);
});
