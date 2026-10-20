import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import {evaluateLocomotion} from "../src/locomotion.mjs";

const scenes=[
  ["carry",JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json",import.meta.url),"utf8"))],
  ["free",JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json",import.meta.url),"utf8"))]
];

test("side-view depth projection cannot create an exaggerated horizontal leg split",()=>{
  for(const [mode,scene] of scenes){
    const depth=scene.character.leg_depth_projection_px;
    assert.ok(depth<=8,"near/far depth projection is too large for side view: "+depth);
    let maxHipGap=0,maxAnkleReach=0;
    for(let frame=0;frame<scene.duration_frames;frame++){
      const p=evaluateLocomotion(scene,frame,mode);
      maxHipGap=Math.max(maxHipGap,Math.abs(p.leftHip.x-p.rightHip.x));
      maxAnkleReach=Math.max(maxAnkleReach,p.diagnostics.ankleClampErrorPx);
    }
    assert.ok(maxHipGap<=5.01,"near/far hip attachment points should visually overlap in profile: "+maxHipGap);
    assert.ok(maxAnkleReach<1.5,"projected leg chain became unreachable: "+maxAnkleReach);
  }
});

test("each leg's depth offset cancels inside its own sagittal-plane chain",()=>{
  for(const [mode,scene] of scenes){
    for(let frame=0;frame<scene.duration_frames;frame++){
      const p=evaluateLocomotion(scene,frame,mode);
      const leftRelative=p.leftFoot.x-p.leftHip.x;
      const rightRelative=p.rightFoot.x-p.rightHip.x;
      assert.ok(Number.isFinite(leftRelative)&&Number.isFinite(rightRelative));
      assert.ok(Math.abs((p.leftHip.x-p.rightHip.x)-2*scene.character.leg_depth_projection_px)<1e-9);
    }
  }
});
