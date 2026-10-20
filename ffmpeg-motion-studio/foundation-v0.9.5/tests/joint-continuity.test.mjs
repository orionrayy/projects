import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { renderSvgFrame } from "../scripts/render-preview.mjs";
import { ACTIVITY_NAMES } from "../src/activity-motion.mjs";

const scenes = [
  JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-free.json", import.meta.url), "utf8")),
  JSON.parse(fs.readFileSync(new URL("../scenes/locomotion-lab.json", import.meta.url), "utf8"))
];
function elementRecords(svg, tag, name) {
  const re = new RegExp("<"+tag+"\\b[^>]*data-anatomy=\\\""+name+"\\\"[^>]*>", "g");
  return [...svg.matchAll(re)].map(m => {
    const attrs=m[0], get=k=>attrs.match(new RegExp(k+'=\\\"([^\\\"]+)\\\"'))?.[1];
    return {attrs, rx:Number(get("rx")), ry:Number(get("ry")), cap:get("data-joint-cap"),
      capWidthRatio:Number(get("data-cap-width-ratio")), capHeightRatio:Number(get("data-cap-height-ratio")),
      fold:get("data-joint-fold")};
  });
}
function allSvgFrames(scene, mode, activity) {
  return [0,Math.floor(scene.duration_frames*0.25),Math.floor(scene.duration_frames*0.5),
    Math.floor(scene.duration_frames*0.75),scene.duration_frames-1]
    .map(frame=>renderSvgFrame(scene,frame,mode,activity));
}

test("elbows have integrated caps sized to the tapered arm, across all action poses",()=>{
  for(const scene of scenes) {
    for(const activity of ACTIVITY_NAMES) {
      const svgList=allSvgFrames({...scene,fps:24,duration_frames:72}, "free", activity);
      for(let idx=0;idx<svgList.length;idx++) {
        const caps=elementRecords(svgList[idx],"ellipse","elbow");
        assert.equal(caps.length,2,activity+" frame sample "+idx+" must render both elbow caps");
        for(const cap of caps) {
          assert.equal(cap.cap,"integrated",activity+" elbow cap annotation");
          assert.ok(cap.rx>=scene.character.elbow_width_px*0.40,
            activity+" elbow cap is too small across the upper/lower segment seam: "+cap.rx);
          assert.ok(cap.ry>=scene.character.elbow_width_px*0.43,
            activity+" elbow cap vertical radius is too small: "+cap.ry);
        }
      }
    }
  }
});

test("knees have integrated caps that hide the sharp segment junction without oversized bulges",()=>{
  for(const scene of scenes) {
    const svg=renderSvgFrame(scene,64,scene.motion.arm_mode||"free","walk");
    const caps=elementRecords(svg,"ellipse","knee");
    assert.equal(caps.length,2);
    for(const cap of caps) {
      assert.equal(cap.cap,"integrated");
      assert.ok(cap.capWidthRatio>=0.22,"knee horizontal cap is too small relative to its own near/far leg width");
      assert.ok(cap.capHeightRatio>=0.27,"knee vertical cap is too small relative to its own near/far leg width");
      assert.ok(cap.capWidthRatio<0.36 && cap.capHeightRatio<0.36,
        "knee cap should blend the segment seam without becoming a spherical bulge");
    }
  }
});

test("elbow crease follows arm geometry instead of remaining horizontal on every pose",()=>{
  for(const scene of scenes) {
    const frames=[renderSvgFrame({...scene,fps:24,duration_frames:72},0,"free","pick-up"),
      renderSvgFrame({...scene,fps:24,duration_frames:72},36,"free","pick-up")];
    const foldPaths=frames.map(svg=>[...svg.matchAll(/<path\b[^>]*data-joint-fold="forearm-normal"[^>]*>/g)].map(m=>m[0]));
    assert.equal(foldPaths[0].length,2);
    assert.equal(foldPaths[1].length,2);
    assert.notDeepEqual(foldPaths[0],foldPaths[1],
      "crease coordinates must respond to the elbow/forearm orientation change");
  }
});
