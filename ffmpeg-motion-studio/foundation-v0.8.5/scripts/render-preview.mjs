import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { evaluateLocomotion } from "../src/locomotion.mjs";

const dir = path.dirname(fileURLToPath(import.meta.url));
const n = (v) => Number.isFinite(v) ? Number(v).toFixed(2) : "0.00";
const deg = (v) => v * 180 / Math.PI;
const dist = (a,b) => Math.hypot(b.x-a.x,b.y-a.y);
const max = (a) => a.length ? Math.max(...a) : 0;
const min = (a) => a.length ? Math.min(...a) : 0;

function seg(a,b,w,color,outline) {
  return '<path d="M '+n(a.x)+' '+n(a.y)+' L '+n(b.x)+' '+n(b.y)+'" fill="none" stroke="'+outline+'" stroke-width="'+(w+4)+'" stroke-linecap="round"/>'+
    '<path d="M '+n(a.x)+' '+n(a.y)+' L '+n(b.x)+' '+n(b.y)+'" fill="none" stroke="'+color+'" stroke-width="'+w+'" stroke-linecap="round"/>';
}
function dot(p,r,fill,outline) {
  return '<circle cx="'+n(p.x)+'" cy="'+n(p.y)+'" r="'+(r+1.6)+'" fill="'+outline+'"/>'+
    '<circle cx="'+n(p.x)+'" cy="'+n(p.y)+'" r="'+r+'" fill="'+fill+'"/>';
}
function taperedLimb(a,b,startWidth,endWidth,fill,outline,highlight="#FFFFFF") {
  const dx=b.x-a.x,dy=b.y-a.y,len=Math.max(1e-6,Math.hypot(dx,dy)),nx=-dy/len,ny=dx/len;
  const ax=a.x+nx*startWidth/2,ay=a.y+ny*startWidth/2,bx=b.x+nx*endWidth/2,by=b.y+ny*endWidth/2;
  const cx=b.x-nx*endWidth/2,cy=b.y-ny*endWidth/2,dx2=a.x-nx*startWidth/2,dy2=a.y-ny*startWidth/2;
  let s='<path data-anatomy="limb" d="M '+n(ax)+' '+n(ay)+' Q '+n(a.x+nx*startWidth*.64)+' '+n(a.y+ny*startWidth*.64)+' '+n(bx)+' '+n(by)+' L '+n(cx)+' '+n(cy)+' Q '+n(a.x-nx*startWidth*.64)+' '+n(a.y-ny*startWidth*.64)+' '+n(dx2)+' '+n(dy2)+' Z" fill="'+fill+'" stroke="'+outline+'" stroke-width="2.7" stroke-linejoin="round"/>';
  s+='<path d="M '+n(a.x+nx*startWidth*.13)+' '+n(a.y+ny*startWidth*.13)+' Q '+n((a.x+b.x)/2+nx*startWidth*.11)+' '+n((a.y+b.y)/2+ny*startWidth*.11)+' '+n(b.x+nx*endWidth*.16)+' '+n(b.y+ny*endWidth*.16)+'" fill="none" stroke="'+highlight+'" stroke-width="1.5" stroke-linecap="round" opacity=".28"/>';
  return s;
}
function legSvg(leg,foot,scene,near) {
  const c=scene.character,color=near?(c.pants||"#35465F"):(c.far_pants||"#56657A");
  let s=taperedLimb(leg.hip,leg.knee,c.thigh_width_px||27,c.knee_width_px||19,color,"#263347");
  s+=taperedLimb(leg.knee,leg.ankle,c.knee_width_px||19,c.ankle_width_px||12,color,"#263347");
  s+='<ellipse data-anatomy="knee" cx="'+n(leg.knee.x)+'" cy="'+n(leg.knee.y)+'" rx="4.5" ry="5.2" fill="'+(near?"#465873":"#66758A")+'" stroke="#263347" stroke-width="1.8"/>';
  s+='<path d="M '+n(leg.hip.x-4)+' '+n(leg.hip.y+9)+' Q '+n(leg.hip.x)+' '+n(leg.hip.y+18)+' '+n(leg.hip.x+5)+' '+n(leg.hip.y+22)+'" fill="none" stroke="#263347" stroke-width="1.1" opacity=".45"/>';
  s+='<g data-anatomy="shoe" transform="translate('+n(foot.x)+' '+n(foot.y-2)+') rotate('+n(deg(foot.angle||0))+')">';
  s+='<path d="M -13 -7 Q -10 -10 -5 -8 L 5 -6 Q 11 -5 15 0 Q 20 3 16 6 Q 12 8 5 7 L -9 6 Q -16 5 -14 -1 Z" fill="#202A3A" stroke="#202A3A" stroke-width="1.8" stroke-linejoin="round"/>';
  s+='<path d="M -9 -6 Q -6 -8 -2 -5 L 6 -3 Q 11 -1 12 2 L -10 2 Z" fill="'+c.shoe+'" stroke="#151E2C" stroke-width="1.1" stroke-linejoin="round"/>';
  s+='<path d="M -12 4 Q 0 6 15 4" stroke="#E9E7DE" stroke-width="1.8" stroke-linecap="round"/><path d="M -5 -3 L 2 -1" stroke="#AAB4C0" stroke-width="1.1" stroke-linecap="round" opacity=".7"/></g>';
  return s;
}
function handSvg(arm,scene,mode,near) {
  const w=arm.wrist,e=arm.elbow,c=scene.character,angle=deg(Math.atan2(w.y-e.y,w.x-e.x));
  let s='<g data-anatomy="hand" data-grip="'+(mode==="carry"?"grip":"relaxed")+'" transform="translate('+n(w.x)+' '+n(w.y)+') rotate('+n(angle)+')">';
  s+='<path d="M -4 -4 Q -2 -7 2 -6 L 6 -3 L 10 -1 Q 13 0 12 2 Q 11 4 7 3 L 5 4 Q 8 6 5 7 Q 3 7 1 5 L -2 3 Q -5 1 -4 -4 Z" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.5" stroke-linejoin="round"/>';
  if(mode==="carry") s+='<path d="M 2 -4 Q 6 -3 9 0 M 2 0 Q 6 1 9 3 M 0 3 Q 3 4 5 6" fill="none" stroke="#925F49" stroke-width="1.05" stroke-linecap="round"/>';
  else s+='<path d="M 4 -3 Q 8 -1 9 2 M 2 0 Q 5 2 6 4 M 0 2 L 2 5 M -3 -3 Q -1 -1 0 1" fill="none" stroke="#925F49" stroke-width="1.0" stroke-linecap="round"/>';
  return s+'</g>';
}
function armSvg(arm,scene,sleeve,near,mode) {
  const c=scene.character;
  let s=taperedLimb(arm.shoulder,arm.elbow,c.upper_arm_width_px||18,c.elbow_width_px||14,sleeve,"#203348");
  s+=taperedLimb(arm.elbow,arm.wrist,c.forearm_width_px||12,c.wrist_width_px||8,c.skin||"#E6B08A","#7B5544");
  s+='<ellipse data-anatomy="elbow" cx="'+n(arm.elbow.x)+'" cy="'+n(arm.elbow.y)+'" rx="4" ry="4.5" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.35"/>';
  s+='<path d="M '+n(arm.elbow.x-4)+' '+n(arm.elbow.y+2)+' Q '+n(arm.elbow.x)+' '+n(arm.elbow.y+5)+' '+n(arm.elbow.x+4)+' '+n(arm.elbow.y+2)+'" fill="none" stroke="#A06E54" stroke-width="1.0" opacity=".8"/>';
  return s+handSvg(arm,scene,mode,near);
}
function headSvg(p,scene) {
  const h=p.head,neck=p.neck,r=scene.character.head_radius_px,c=scene.character,rx=r*.84,ry=r*1.03;
  let s='<g data-anatomy="head" transform="rotate('+n(deg(p.headAngle))+' '+n(neck.x)+' '+n(neck.y)+')">';
  s+='<ellipse cx="'+n(h.x-rx*.91)+'" cy="'+n(h.y+1)+'" rx="3.6" ry="5.2" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.2"/><ellipse cx="'+n(h.x+rx*.91)+'" cy="'+n(h.y+1)+'" rx="3.6" ry="5.2" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.2"/>';
  s+='<ellipse cx="'+n(h.x)+'" cy="'+n(h.y)+'" rx="'+n(rx+1.4)+'" ry="'+n(ry+1.4)+'" fill="#6D4A3D"/><ellipse cx="'+n(h.x)+'" cy="'+n(h.y)+'" rx="'+n(rx)+'" ry="'+n(ry)+'" fill="'+c.skin+'"/>';
  s+='<path d="M '+n(h.x-rx+1)+' '+n(h.y-3)+' C '+n(h.x-rx-2)+' '+n(h.y-ry*.76)+', '+n(h.x-rx*.25)+' '+n(h.y-ry*1.16)+', '+n(h.x+rx*.28)+' '+n(h.y-ry*1.04)+' C '+n(h.x+rx*.83)+' '+n(h.y-ry*.99)+', '+n(h.x+rx+1)+' '+n(h.y-ry*.55)+', '+n(h.x+rx-1)+' '+n(h.y-3)+' L '+n(h.x+rx*.64)+' '+n(h.y-8)+' Q '+n(h.x+4)+' '+n(h.y-18)+' '+n(h.x-5)+' '+n(h.y-12)+' Q '+n(h.x-12)+' '+n(h.y-7)+' '+n(h.x-rx+1)+' '+n(h.y-3)+' Z" fill="'+c.hair+'"/>';
  s+='<path d="M '+n(h.x-13)+' '+n(h.y-6)+' q 4 -2 8 0 M '+n(h.x+4)+' '+n(h.y-6)+' q 4 -2 8 0" fill="none" stroke="#5C4034" stroke-width="1.7" stroke-linecap="round"/>';
  s+='<ellipse cx="'+n(h.x-8.4)+'" cy="'+n(h.y-1)+'" rx="2.3" ry="3.0" fill="#252A31"/><ellipse cx="'+n(h.x+8.4)+'" cy="'+n(h.y-1)+'" rx="2.3" ry="3.0" fill="#252A31"/><circle cx="'+n(h.x-9.1)+'" cy="'+n(h.y-2.1)+'" r=".8" fill="#FFFDF6"/><circle cx="'+n(h.x+7.7)+'" cy="'+n(h.y-2.1)+'" r=".8" fill="#FFFDF6"/>';
  s+='<path d="M '+n(h.x)+' '+n(h.y+1)+' l -1.5 5.5 l 3.4 1.1 M '+n(h.x-6)+' '+n(h.y+12)+' Q '+n(h.x)+' '+n(h.y+15)+' '+n(h.x+6.5)+' '+n(h.y+11.7)+'" fill="none" stroke="#8D5144" stroke-width="1.45" stroke-linecap="round"/>';
  s+='<ellipse cx="'+n(h.x-12)+'" cy="'+n(h.y+7)+'" rx="3" ry="1.6" fill="#CF8A78" opacity=".23"/><ellipse cx="'+n(h.x+12)+'" cy="'+n(h.y+7)+'" rx="3" ry="1.6" fill="#CF8A78" opacity=".23"/>';
  return s+'</g>';
}
function neckSvg(p,scene) {
  const c=scene.character,top=p.neck,bottom={x:p.chest.x,y:p.chest.y-2};
  return '<path data-anatomy="neck" d="M '+n(top.x-5)+' '+n(top.y)+' Q '+n(top.x)+' '+n(top.y-1)+' '+n(top.x+5)+' '+n(top.y)+' L '+n(bottom.x+8)+' '+n(bottom.y)+' Q '+n(bottom.x)+' '+n(bottom.y+5)+' '+n(bottom.x-8)+' '+n(bottom.y)+' Z" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.6" stroke-linejoin="round"/>'+
    '<path data-anatomy="collar" d="M '+n(bottom.x-11)+' '+n(bottom.y+2)+' Q '+n(bottom.x)+' '+n(bottom.y+10)+' '+n(bottom.x+11)+' '+n(bottom.y+2)+'" fill="none" stroke="#203348" stroke-width="2.6" stroke-linecap="round"/>';
}
function basketSvg(p,scene) {
  const b=p.basket,prop=scene.prop,cx=b.x+b.width/2,cy=b.y+b.height/2;
  let s='<g transform="rotate('+n(b.angleDegrees||0)+' '+n(cx)+' '+n(cy)+')">';
  s+='<path d="M '+n(cx-prop.handle_spacing_px/2)+' '+n(b.y+4)+' Q '+n(cx)+' '+n(b.y-17)+' '+n(cx+prop.handle_spacing_px/2)+' '+n(b.y+4)+'" fill="none" stroke="'+prop.handle_color+'" stroke-width="5" stroke-linecap="round"/>';
  s+='<path d="M '+n(b.x+2)+' '+n(b.y+8)+' Q '+n(cx)+' '+n(b.y+12)+' '+n(b.x+b.width-2)+' '+n(b.y+8)+' L '+n(b.x+b.width-8)+' '+n(b.y+b.height)+' Q '+n(cx)+' '+n(b.y+b.height+3)+' '+n(b.x+7)+' '+n(b.y+b.height)+' Z" fill="'+prop.basket_color+'" stroke="#8A542C" stroke-width="2.2"/>';
  s+='<path d="M '+n(b.x+7)+' '+n(b.y+19)+' L '+n(b.x+b.width-7)+' '+n(b.y+19)+' M '+n(b.x+9)+' '+n(b.y+29)+' L '+n(b.x+b.width-9)+' '+n(b.y+29)+'" stroke="#C87528" stroke-width="2"/>';
  s+='<rect x="'+n(b.x+2)+'" y="'+n(b.y+6)+'" width="'+n(b.width-4)+'" height="7" rx="3.5" fill="#B96D2A" stroke="#8A542C" stroke-width="1.2"/>';
  return s+'</g>';
}
export function renderSvgFrame(scene,frameIndex,armMode) {
  const mode=armMode||scene.motion.arm_mode||"carry";
  if(mode!=="carry"&&mode!=="free") throw new RangeError("Unsupported render arm mode.");
  const p=evaluateLocomotion(scene,frameIndex,mode),floor=scene.background.horizon_y,c=scene.character;
  let s='<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="'+scene.canvas.width+'" height="'+scene.canvas.height+'" viewBox="0 0 '+scene.canvas.width+' '+scene.canvas.height+'" role="img">';
  s+='<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBFAF3"/><stop offset="1" stop-color="'+scene.background.color+'"/></linearGradient></defs>';
  s+='<rect width="100%" height="100%" fill="url(#sky)"/><circle cx="1080" cy="140" r="74" fill="#E5E2D6" opacity=".35"/>';
  s+='<path d="M 0 '+n(floor)+' L '+scene.canvas.width+' '+n(floor)+' L '+scene.canvas.width+' '+scene.canvas.height+' L 0 '+scene.canvas.height+' Z" fill="'+scene.background.floor+'"/>';
  s+='<path d="M 0 '+n(floor)+' L '+scene.canvas.width+' '+n(floor)+'" stroke="#C7C0B0" stroke-width="2"/>';
  for(let i=0;i<11;i++){const x=i*145+22;s+='<path d="M '+x+' '+(floor+24)+' L '+(x+70)+' '+(floor+24)+'" stroke="#D8D2C3" stroke-width="1"/>';}
  s+='<ellipse cx="'+n(p.pelvis.x+12)+'" cy="'+n(floor+5)+'" rx="63" ry="9" fill="#9C988B" opacity=".22"/>';
  s+=legSvg(p.rightLeg,p.rightFoot,scene,false)+legSvg(p.leftLeg,p.leftFoot,scene,true);
  s+=armSvg(p.farArm,scene,"#2F6D8D",false,mode);
  const pel=p.pelvis,chest=p.chest,near=p.shoulders.near,far=p.shoulders.far;
  const sh=c.shoulder_half_width_px||23,hip=c.pelvis_half_width_px||22;
  s+='<path data-anatomy="torso" d="M '+n(chest.x-sh-8)+' '+n(chest.y+7)+' Q '+n(chest.x-sh-14)+' '+n(chest.y+20)+' '+n(chest.x-22)+' '+n(chest.y+42)+' L '+n(chest.x-17)+' '+n(pel.y-6)+' Q '+n(pel.x-hip*.65)+' '+n(pel.y+6)+' '+n(pel.x-hip)+' '+n(pel.y+5)+' Q '+n(pel.x)+' '+n(pel.y+15)+' '+n(pel.x+hip)+' '+n(pel.y+5)+' Q '+n(pel.x+hip*.65)+' '+n(pel.y+6)+' '+n(chest.x+17)+' '+n(pel.y-6)+' L '+n(chest.x+22)+' '+n(chest.y+42)+' Q '+n(chest.x+sh+14)+' '+n(chest.y+20)+' '+n(chest.x+sh+8)+' '+n(chest.y+7)+' Q '+n(chest.x+sh*.45)+' '+n(chest.y-5)+' '+n(chest.x)+' '+n(chest.y-4)+' Q '+n(chest.x-sh*.45)+' '+n(chest.y-5)+' '+n(chest.x-sh-8)+' '+n(chest.y+7)+' Z" fill="'+c.shirt+'" stroke="#203348" stroke-width="2.7" stroke-linejoin="round"/>';
  s+='<path d="M '+n(chest.x-14)+' '+n(chest.y+13)+' Q '+n(chest.x)+' '+n(chest.y+21)+' '+n(chest.x+14)+' '+n(chest.y+13)+'" fill="none" stroke="'+c.shirt_shadow+'" stroke-width="2.3" stroke-linecap="round" opacity=".9"/>';
  s+='<path d="M '+n(chest.x-5)+' '+n(chest.y+24)+' Q '+n(chest.x-1)+' '+n(chest.y+40)+' '+n(chest.x-4)+' '+n(chest.y+53)+'" fill="none" stroke="#DCE9EC" stroke-width="1.3" opacity=".22"/>';
  s+='<path data-anatomy="waistband" d="M '+n(pel.x-hip)+' '+n(pel.y+6)+' Q '+n(pel.x)+' '+n(pel.y+13)+' '+n(pel.x+hip)+' '+n(pel.y+6)+'" fill="none" stroke="#263347" stroke-width="2.6"/>';
  s+=neckSvg(p,scene);
  s+=headSvg(p,scene); if(mode==="carry") s+=basketSvg(p,scene); s+=armSvg(p.nearArm,scene,"#3A82A3",true,mode);
  s+='<rect x="34" y="28" width="388" height="82" rx="14" fill="#FFFEFA" opacity=".92" stroke="#DAD5C7"/>';
  s+='<text x="54" y="57" font-family="DejaVu Sans,sans-serif" font-size="18" font-weight="700" fill="#243345">MOTION STUDIO / v0.8.5</text>';
  s+='<text x="54" y="82" font-family="DejaVu Sans,sans-serif" font-size="14" fill="#526173">'+(mode==="carry"?"Carry interaction + hand contact":"Free-arm counter-swing")+'</text>';
  s+='<text x="54" y="99" font-family="DejaVu Sans,sans-serif" font-size="11" fill="#697687">FRAME '+String(frameIndex+1).padStart(3,"0")+' / '+scene.duration_frames+' TIME '+n(p.timeSeconds)+' s</text>';
  s+='<text x="34" y="690" font-family="DejaVu Sans,sans-serif" font-size="12" fill="#716B60">Geometry diagnostics are not an artistic-naturalness score.</text>';
  s+='<text x="'+(scene.canvas.width-34)+'" y="690" text-anchor="end" font-family="DejaVu Sans,sans-serif" font-size="12" fill="#716B60">24 FPS · Procedural 2D preview</text></svg>';
  return s;
}
export function summarizeScene(scene, armMode) {
  const mode = armMode || scene.motion.arm_mode || "carry";
  const c = scene.character, m = scene.motion;
  const poses = [];
  for (let i = 0; i < scene.duration_frames; i++) poses.push(evaluateLocomotion(scene, i, mode));
  const vals = (fn) => poses.map(fn);
  const range = (xs) => Math.max(...xs) - Math.min(...xs);
  const step = (points) => {
    let out = 0;
    for (let i = 1; i < points.length; i++) out = Math.max(out, dist(points[i - 1], points[i]));
    return out;
  };
  const acceleration = (points) => {
    let out = 0;
    for (let i = 2; i < points.length; i++) {
      const a = points[i - 2], b = points[i - 1], c = points[i];
      out = Math.max(out, Math.hypot(c.x - 2 * b.x + a.x, c.y - 2 * b.y + a.y));
    }
    return out;
  };
  const pointSeries = {
    pelvis: vals((p) => p.pelvis),
    chest: vals((p) => p.chest),
    head: vals((p) => p.head),
    nearElbow: vals((p) => p.nearArm.elbow),
    farElbow: vals((p) => p.farArm.elbow),
    nearWrist: vals((p) => p.nearArm.wrist),
    farWrist: vals((p) => p.farArm.wrist),
    leftKnee: vals((p) => p.leftLeg.knee),
    rightKnee: vals((p) => p.rightLeg.knee),
    leftFoot: vals((p) => p.leftFoot),
    rightFoot: vals((p) => p.rightFoot)
  };
  const sep = vals((p) => p.leftFoot.x - p.rightFoot.x);
  const torso = vals((p) => deg(p.torsoAngle));
  const head = vals((p) => deg(p.headAngle));
  const nearWristRelative = vals((p) => p.nearArm.wrist.x - p.rootX);
  const farWristRelative = vals((p) => p.farArm.wrist.x - p.rootX);
  const finite = poses.every((p) => [
    p.rootX,p.pelvis.x,p.pelvis.y,p.chest.x,p.chest.y,p.head.x,p.head.y,
    p.nearArm.elbow.x,p.nearArm.elbow.y,p.farArm.elbow.x,p.farArm.elbow.y,
    p.leftFoot.x,p.leftFoot.y,p.rightFoot.x,p.rightFoot.y,
    p.diagnostics.boneLengthErrorPx,p.diagnostics.basketContactErrorPx,p.diagnostics.groundPenetrationPx
  ].every(Number.isFinite));
  if (!finite) throw new Error("Non-finite pose value detected during preview preflight.");

  let maxStanceFootDriftPerFramePx = 0, stanceFootSamplePairs = 0, stanceTransitions = 0;
  for (let i = 1; i < poses.length; i++) {
    for (const side of ["left", "right"]) {
      const prev = poses[i - 1][side + "Foot"], curr = poses[i][side + "Foot"];
      if (prev.inStance !== curr.inStance) stanceTransitions++;
      if (prev.inStance && curr.inStance) {
        maxStanceFootDriftPerFramePx = Math.max(maxStanceFootDriftPerFramePx, Math.hypot(curr.x - prev.x, curr.y - prev.y));
        stanceFootSamplePairs++;
      }
    }
  }
  const pointSteps = Object.fromEntries(Object.entries(pointSeries).map(([k, series]) => [k, step(series)]));
  const pointAccelerations = Object.fromEntries(Object.entries(pointSeries).map(([k, series]) => [k, acceleration(series)]));
  const maxJointAccelerationPxPerFrame2 = Math.max(...Object.values(pointAccelerations));
  const temporalDiagnostics = {
    maxPelvisStepPx: pointSteps.pelvis,
    maxChestStepPx: pointSteps.chest,
    maxHeadStepPx: pointSteps.head,
    maxNearElbowStepPx: pointSteps.nearElbow,
    maxFarElbowStepPx: pointSteps.farElbow,
    maxNearWristStepPx: pointSteps.nearWrist,
    maxFarWristStepPx: pointSteps.farWrist,
    maxKneeStepPx: Math.max(pointSteps.leftKnee, pointSteps.rightKnee),
    maxJointAccelerationPxPerFrame2,
    jointAccelerationByPointPxPerFrame2: pointAccelerations,
    maxStanceFootDriftPerFramePx,
    stanceFootSamplePairs,
    stanceTransitions,
    allTemporalMetricsFinite: Object.values(pointSteps).concat(Object.values(pointAccelerations), [maxStanceFootDriftPerFramePx]).every(Number.isFinite)
  };
  return {
    schemaVersion:"1.0.0", sceneId:scene.scene_id, sceneVersion:scene.scene_version,
    armMode:mode, frameCount:scene.duration_frames, fps:scene.fps, durationSeconds:scene.duration_frames/scene.fps,
    canvas:scene.canvas, deterministicPoseSampling:true, allPoseValuesFinite:finite,
    minProjectedFootSeparationPx:Math.min(...sep),
    maxBoneLengthErrorPx:Math.max(...vals((p)=>p.diagnostics.boneLengthErrorPx)),
    maxBasketContactErrorPx:Math.max(...vals((p)=>p.diagnostics.basketContactErrorPx)),
    maxGroundPenetrationPx:Math.max(...vals((p)=>p.diagnostics.groundPenetrationPx)),
    maxAnkleClampErrorPx:Math.max(...vals((p)=>p.diagnostics.ankleClampErrorPx)),
    torsoAngleRangeDegrees:range(torso), headAngleRangeDegrees:range(head), basketTiltRangeDegrees:range(vals((p)=>p.basket.angleDegrees||0)),
    nearArmWristRelativeRangePx:range(nearWristRelative), farArmWristRelativeRangePx:range(farWristRelative),
    anatomyDiagnostics: {
      headHeightPx: c.head_radius_px * 2.06,
      torsoHeightPx: m.torso_length_px || 70,
      neckLengthPx: dist(poses[0].neck, {x:poses[0].chest.x,y:poses[0].chest.y-2}),
      torsoToHeadRatio: (m.torso_length_px || 70) / (c.head_radius_px * 2.06),
      neckToHeadRatio: dist(poses[0].neck, {x:poses[0].chest.x,y:poses[0].chest.y-2}) / (c.head_radius_px * 2.06),
      legToTorsoRatio: (c.upper_leg_px + c.lower_leg_px) / (m.torso_length_px || 70),
      statureInHeadUnits: (scene.background.horizon_y - (poses[0].head.y - c.head_radius_px * 1.03)) / (c.head_radius_px * 2.06),
      shoulderHalfWidthPx: c.shoulder_half_width_px || 15,
      hipHalfWidthPx: c.pelvis_half_width_px || 22
    },
    minNearArmElbowAngleDegrees:Math.min(...vals((p)=>p.nearArm.elbowAngleDegrees)),
    maxNearArmElbowAngleDegrees:Math.max(...vals((p)=>p.nearArm.elbowAngleDegrees)),
    temporalDiagnostics,
    humanVisualAcceptance:"pending", pixelLevelNaturalnessMeasurement:"not_performed",
    browserFfmpegRasterParity:"not_verified",
    note:"Frame-step, acceleration and stance-drift checks detect some temporal defects; passing metrics do not establish natural motion, artistic quality, or production readiness."
  };
}

export function renderScenePreview(scene,outputDir,armMode) {
  const mode=armMode||scene.motion.arm_mode||"carry",frameDir=path.join(outputDir,".working",mode);
  fs.mkdirSync(frameDir,{recursive:true});
  for(let i=0;i<scene.duration_frames;i++) fs.writeFileSync(path.join(frameDir,"frame-"+String(i).padStart(4,"0")+".svg"),renderSvgFrame(scene,i,mode),"utf8");
  const report=summarizeScene(scene,mode);
  fs.mkdirSync(outputDir,{recursive:true});
  fs.writeFileSync(path.join(outputDir,mode+"-metrics.json"),JSON.stringify(report,null,2)+"\n","utf8");
  return {frameDir,summary:report};
}
function run() {
  const out=path.resolve(process.argv[2]||".motion-studio-preview");
  const carry=JSON.parse(fs.readFileSync(path.join(dir,"..","scenes","locomotion-lab.json"),"utf8"));
  const free=JSON.parse(fs.readFileSync(path.join(dir,"..","scenes","locomotion-free.json"),"utf8"));
  const results=[renderScenePreview(carry,out,"carry"),renderScenePreview(free,out,"free")];
  const manifest={schemaVersion:"1.1.0",generator:"Motion Studio v0.8.5 anatomical SVG preview",producedAt:"deterministic-build",scenes:results.map(x=>x.summary),productionStatus:"prototype",visualReviewRequired:true};
  fs.writeFileSync(path.join(out,"render-manifest.json"),JSON.stringify(manifest,null,2)+"\n","utf8");
  process.stdout.write(JSON.stringify({outputDir:out,scenes:manifest.scenes.map(x=>({mode:x.armMode,frames:x.frameCount,durationSeconds:x.durationSeconds,finite:x.allPoseValuesFinite}))},null,2)+"\n");
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) run();
