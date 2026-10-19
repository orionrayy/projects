import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {evaluateLocomotion} from "../src/locomotion.mjs";

const carry=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json",import.meta.url),"utf8"));
const free=JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json",import.meta.url),"utf8"));
const midpoint=(a,b)=>({x:(a.x+b.x)/2,y:(a.y+b.y)/2});
const distance=(a,b)=>Math.hypot(a.x-b.x,a.y-b.y);
function gaitMetrics(scene,mode){
  const stanceAngles=[],swingAngles=[],stanceBends=[],swingBends=[];
  let maxAnkleClamp=0,maxBoneError=0;
  for(let i=0;i<scene.duration_frames;i++){
    const p=evaluateLocomotion(scene,i,mode);
    maxAnkleClamp=Math.max(maxAnkleClamp,p.diagnostics.ankleClampErrorPx);
    maxBoneError=Math.max(maxBoneError,p.diagnostics.boneLengthErrorPx);
    for(const [foot,leg] of [[p.leftFoot,p.leftLeg],[p.rightFoot,p.rightLeg]]){
      const bend=distance(leg.knee,midpoint(leg.hip,leg.ankle));
      if(foot.inStance){stanceAngles.push(leg.jointAngleDegrees);stanceBends.push(bend);}
      else {swingAngles.push(leg.jointAngleDegrees);swingBends.push(bend);}
    }
  }
  const mean=xs=>xs.reduce((a,b)=>a+b,0)/Math.max(xs.length,1);
  return {minStanceAngle:Math.min(...stanceAngles),meanStanceAngle:mean(stanceAngles),meanSwingAngle:mean(swingAngles),
    meanStanceBend:mean(stanceBends),meanSwingBend:mean(swingBends),maxAnkleClamp,maxBoneError};
}

test("stance legs extend while swing legs flex in carry and free-arm profiles",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const g=gaitMetrics(scene,mode);
    assert.ok(g.minStanceAngle>148,"stance knees remain too crouched: "+JSON.stringify(g));
    assert.ok(g.meanStanceAngle>g.meanSwingAngle+10,"stance/swing angles lack separation: "+JSON.stringify(g));
    assert.ok(g.meanStanceBend<g.meanSwingBend*.72,"stance legs bend too much relative to swing: "+JSON.stringify(g));
    assert.ok(g.maxAnkleClamp<1.5,"ankle target became unreachable: "+JSON.stringify(g));
    assert.ok(g.maxBoneError<0.02,"bone length error: "+JSON.stringify(g));
  }
});

test("phase-aware knee pole is deterministic and approximately repeats each gait cycle",()=>{
  for(const [scene,mode] of [[carry,"carry"],[free,"free"]]){
    const a=evaluateLocomotion(scene,0,mode);
    const cycleFrame=Math.round(scene.motion.cycle_seconds*scene.fps);
    const b=evaluateLocomotion(scene,cycleFrame,mode);
    const localA={x:a.leftLeg.knee.x-a.rootX,y:a.leftLeg.knee.y-a.pelvis.y};
    const localB={x:b.leftLeg.knee.x-b.rootX,y:b.leftLeg.knee.y-b.pelvis.y};
    assert.equal(a.leftFoot.inStance,true);
    assert.ok(Number.isFinite(a.leftLeg.knee.x)&&Number.isFinite(a.leftLeg.knee.y));
    assert.ok(distance(localA,localB)<8,"knee trajectory should repeat smoothly by phase: "+JSON.stringify({localA,localB}));
    assert.ok(distance(a.leftLeg.knee,evaluateLocomotion(scene,0,mode).leftLeg.knee)<1e-9);
  }
});
