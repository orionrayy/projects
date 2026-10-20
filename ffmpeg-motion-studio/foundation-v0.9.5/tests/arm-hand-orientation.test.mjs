import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { ACTIVITY_NAMES, evaluateActivity } from "../src/activity-motion.mjs";
import { renderSvgFrame } from "../scripts/render-preview.mjs";

const source = JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8"));
const scene = { ...source, fps: 24, duration_frames: 72 };
const angleDelta = (a,b) => Math.atan2(Math.sin(a-b), Math.cos(a-b));
const cross = (root, end, point) =>
  (end.x-root.x)*(point.y-root.y) - (end.y-root.y)*(point.x-root.x);
function handRecords(svg) {
  return [...svg.matchAll(/<g data-anatomy="hand"([^>]*)>/g)].map(m => {
    const attrs = m[1];
    const get = key => attrs.match(new RegExp(key+'="([^"]*)"'))?.[1];
    return { attrs, side:get("data-hand-side"), pose:get("data-hand-pose"),
      orientation:get("data-hand-orientation"), mirror:get("data-hand-mirror"),
      angle:Number(get("data-hand-angle-degrees")), transform:get("transform")||"" };
  });
}
function radians(degrees) { return degrees * Math.PI / 180; }

test("near and far elbow branches remain anatomically separated through every activity", () => {
  for (const activity of ACTIVITY_NAMES) {
    for (let frame=0; frame<scene.duration_frames; frame++) {
      const p=evaluateActivity(scene,frame,activity,"free");
      for (const [arm,expected,side] of [[p.nearArm,1,"near"],[p.farArm,-1,"far"]]) {
        const signedArea=cross(arm.shoulder,arm.wrist,arm.elbow);
        if (Math.abs(signedArea)>1) {
          assert.ok(signedArea*expected>0,
            activity+" frame "+frame+" "+side+" elbow switched sides of its shoulder-wrist axis: "+signedArea.toFixed(3));
        }
        const upper=Math.hypot(arm.elbow.x-arm.shoulder.x,arm.elbow.y-arm.shoulder.y);
        const lower=Math.hypot(arm.wrist.x-arm.elbow.x,arm.wrist.y-arm.elbow.y);
        assert.ok(Math.abs(upper-scene.character.upper_arm_px)<0.02, activity+" "+side+" upper-arm length drift");
        assert.ok(Math.abs(lower-scene.character.forearm_px)<0.02, activity+" "+side+" forearm length drift");
      }
    }
  }
});

test("hands never use a depth-layer reflection that reverses the palm/thumb", () => {
  for (const activity of ACTIVITY_NAMES) {
    for (let frame=0; frame<scene.duration_frames; frame++) {
      const hands=handRecords(renderSvgFrame(scene,frame,"free",activity));
      assert.equal(hands.length,2,activity+" frame "+frame+" should render exactly two hands");
      assert.deepEqual(hands.map(h=>h.side).sort(),["far","near"]);
      for (const hand of hands) {
        assert.equal(hand.mirror,"none",activity+" frame "+frame+" "+hand.side+" hand must not be reflected");
        assert.doesNotMatch(hand.transform,/scale\([^)]*-[0-9]/,
          activity+" frame "+frame+" "+hand.side+" hand has a negative scale");
        assert.ok(Number.isFinite(hand.angle),activity+" frame "+frame+" "+hand.side+" hand angle is not finite");
        assert.ok(["gravity-down","target-directed","object-directed","forearm-following"].includes(hand.orientation),
          activity+" frame "+frame+" unexpected hand orientation "+hand.orientation);
      }
    }
  }
});

test("relaxed hands stay gravity-directed and interaction hands align to their target", () => {
  for (const activity of ["stand","look-around","turn-in-place"]) {
    for (let frame=0; frame<scene.duration_frames; frame++) {
      for (const hand of handRecords(renderSvgFrame(scene,frame,"free",activity))) {
        assert.equal(hand.orientation,"gravity-down",activity+" relaxed "+hand.side+" hand orientation");
        assert.ok(Math.abs(angleDelta(radians(hand.angle),Math.PI/2))<0.57,
          activity+" frame "+frame+" "+hand.side+" relaxed hand no longer points down");
      }
    }
  }

  for (let frame=0; frame<scene.duration_frames; frame++) {
    const p=evaluateActivity(scene,frame,"reach","free");
    const hand=handRecords(renderSvgFrame(scene,frame,"free","reach")).find(h=>h.side==="near");
    const weight=p.activityState.reachWeight||0;
    if(weight<0.22) {
      assert.equal(hand.pose,"relaxed","reach should begin from a relaxed hand pose");
      assert.equal(hand.orientation,"gravity-down");
    } else {
      assert.equal(hand.orientation,"target-directed");
      const targetAngle=Math.atan2(p.activityState.reachTarget.y-p.nearArm.wrist.y,
        p.activityState.reachTarget.x-p.nearArm.wrist.x);
      assert.ok(Math.abs(angleDelta(radians(hand.angle),targetAngle))<=0.42,
        "reach hand must point from the wrist toward the button at frame "+frame);
    }
    if(p.activityState.reachTarget.active) {
      const tip={x:p.nearArm.wrist.x+17*Math.cos(radians(hand.angle)),
        y:p.nearArm.wrist.y+17*Math.sin(radians(hand.angle))};
      assert.ok(Math.hypot(tip.x-p.activityState.reachTarget.x,tip.y-p.activityState.reachTarget.y)<1e-6,
        "press fingertip must touch the visible target at frame "+frame);
      assert.ok(p.diagnostics.reachTargetContactErrorPx<1e-8,
        "contact metric must measure fingertip, not wrist, at frame "+frame);
    }
  }

  const p=evaluateActivity(scene,71,"pick-up","free");
  const hand=handRecords(renderSvgFrame(scene,71,"free","pick-up")).find(h=>h.side==="near");
  assert.equal(hand.pose,"grip");
  assert.equal(hand.orientation,"object-directed");
  const objectAngle=Math.atan2(p.activityState.pickupItem.y-p.nearArm.wrist.y,
    p.activityState.pickupItem.x-p.nearArm.wrist.x);
  assert.ok(Math.abs(angleDelta(radians(hand.angle),objectAngle))<=0.80,
    "grip palm should be oriented toward the held object");
});

test("hand rotation has no frame-to-frame half-turn discontinuity", () => {
  for (const activity of ACTIVITY_NAMES) {
    const previous={near:null,far:null};
    for (let frame=0; frame<scene.duration_frames; frame++) {
      const hands=handRecords(renderSvgFrame(scene,frame,"free",activity));
      for (const hand of hands) {
        if (previous[hand.side]!==null) {
          const step=Math.abs(angleDelta(radians(hand.angle),previous[hand.side]));
          assert.ok(step<Math.PI/2,
            activity+" frame "+frame+" "+hand.side+" hand rotation jumps "+(step*180/Math.PI).toFixed(1)+" degrees");
        }
        previous[hand.side]=radians(hand.angle);
      }
    }
  }
});

test("reach contact is measured at the fingertip and begins from rest", () => {
  const initial=evaluateActivity(scene,0,"reach","free");
  const initialHand=handRecords(renderSvgFrame(scene,0,"free","reach")).find(h=>h.side==="near");
  assert.equal(initialHand.pose,"relaxed");
  assert.equal(initial.activityState.reachTarget.active,false);
  const contactFrames=[];
  for(let frame=0;frame<scene.duration_frames;frame++) {
    const p=evaluateActivity(scene,frame,"reach","free");
    if(p.activityState.reachTarget.active) contactFrames.push(frame);
  }
  assert.ok(contactFrames.length>=5,"a stable multi-frame contact should be visible, not a one-frame flash");
  for(const frame of contactFrames) {
    const p=evaluateActivity(scene,frame,"reach","free");
    const hand=handRecords(renderSvgFrame(scene,frame,"free","reach")).find(h=>h.side==="near");
    const tip={x:p.nearArm.wrist.x+17*Math.cos(radians(hand.angle)),
      y:p.nearArm.wrist.y+17*Math.sin(radians(hand.angle))};
    assert.ok(Math.hypot(tip.x-p.activityState.reachTarget.x,tip.y-p.activityState.reachTarget.y)<1e-6);
  }
});
