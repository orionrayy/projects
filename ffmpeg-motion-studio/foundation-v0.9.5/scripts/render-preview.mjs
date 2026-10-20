import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { evaluateLocomotion } from "../src/locomotion.mjs";
import { evaluateActivity, ACTIVITY_LABELS } from "../src/activity-motion.mjs";

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
function organicLimb(a,b,startWidth,endWidth,fill,outline,options={}) {
  const dx=b.x-a.x,dy=b.y-a.y,len=Math.max(1e-6,Math.hypot(dx,dy)),nx=-dy/len,ny=dx/len;
  const midWidth=Math.max(startWidth,endWidth)*(options.midBulgeFactor||1.08);
  const p=(t,off)=>({x:a.x+dx*t+nx*off,y:a.y+dy*t+ny*off});
  const ap=p(0,startWidth/2),am=p(0,-startWidth/2),mp=p(.5,midWidth/2),mm=p(.5,-midWidth/2),bp=p(1,endWidth/2),bm=p(1,-endWidth/2);
  const cp1p=p(.22,startWidth*.56),cp2p=p(.41,midWidth*.53),cp3p=p(.61,midWidth*.53),cp4p=p(.86,endWidth*.58);
  const cp1m=p(.86,-endWidth*.58),cp2m=p(.61,-midWidth*.53),cp3m=p(.41,-midWidth*.53),cp4m=p(.22,-startWidth*.56);
  let s='<path data-anatomy="limb" data-contour="organic" d="M '+n(ap.x)+' '+n(ap.y)+' C '+n(cp1p.x)+' '+n(cp1p.y)+' '+n(cp2p.x)+' '+n(cp2p.y)+' '+n(mp.x)+' '+n(mp.y)+' C '+n(cp3p.x)+' '+n(cp3p.y)+' '+n(cp4p.x)+' '+n(cp4p.y)+' '+n(bp.x)+' '+n(bp.y)+' L '+n(bm.x)+' '+n(bm.y)+' C '+n(cp1m.x)+' '+n(cp1m.y)+' '+n(cp2m.x)+' '+n(cp2m.y)+' '+n(mm.x)+' '+n(mm.y)+' C '+n(cp3m.x)+' '+n(cp3m.y)+' '+n(cp4m.x)+' '+n(cp4m.y)+' '+n(am.x)+' '+n(am.y)+' Z" fill="'+fill+'" stroke="'+outline+'" stroke-width="2.45" stroke-linejoin="round"/>';
  const h0=p(0,startWidth*.17),hm=p(.5,midWidth*.18),h1=p(1,endWidth*.17),hcp1=p(.22,startWidth*.22),hcp2=p(.41,midWidth*.20),hcp3=p(.61,midWidth*.20),hcp4=p(.86,endWidth*.22);
  s+='<path data-anatomy="limb-highlight" d="M '+n(h0.x)+' '+n(h0.y)+' C '+n(hcp1.x)+' '+n(hcp1.y)+' '+n(hcp2.x)+' '+n(hcp2.y)+' '+n(hm.x)+' '+n(hm.y)+' C '+n(hcp3.x)+' '+n(hcp3.y)+' '+n(hcp4.x)+' '+n(hcp4.y)+' '+n(h1.x)+' '+n(h1.y)+'" fill="none" stroke="#FFFFFF" stroke-width="1.25" stroke-linecap="round" opacity=".3"/>';
  const shade0=p(0,-startWidth*.28),shadem=p(.5,-midWidth*.29),shade1=p(1,-endWidth*.28),scp1=p(.22,-startWidth*.30),scp2=p(.41,-midWidth*.31),scp3=p(.61,-midWidth*.31),scp4=p(.86,-endWidth*.30);
  s+='<path data-anatomy="limb-shade" d="M '+n(shade0.x)+' '+n(shade0.y)+' C '+n(scp1.x)+' '+n(scp1.y)+' '+n(scp2.x)+' '+n(scp2.y)+' '+n(shadem.x)+' '+n(shadem.y)+' C '+n(scp3.x)+' '+n(scp3.y)+' '+n(scp4.x)+' '+n(scp4.y)+' '+n(shade1.x)+' '+n(shade1.y)+'" fill="none" stroke="'+outline+'" stroke-width="1.15" stroke-linecap="round" opacity=".18"/>';
  return s;
}
function legSvg(leg,foot,scene,near) {
  const c=scene.character,color=near?(c.pants||"#35465F"):(c.far_pants||"#4B596D");
  const thigh=near?(c.thigh_width_px||27):(c.far_thigh_width_px||18),knee=near?(c.knee_width_px||19):(c.far_knee_width_px||13),ankle=near?(c.ankle_width_px||12):(c.far_ankle_width_px||9);
  let s='<g data-anatomy="leg-chain" data-leg-depth="'+(near?"near":"far")+'">';
  s+=organicLimb(leg.hip,leg.knee,thigh,knee,color,"#263347",{midBulgeFactor:1.1})+organicLimb(leg.knee,leg.ankle,knee,ankle,color,"#263347",{midBulgeFactor:1.11});
  s+='<ellipse data-anatomy="knee" cx="'+n(leg.knee.x)+'" cy="'+n(leg.knee.y)+'" rx="'+n(knee*.16)+'" ry="'+n(knee*.19)+'" fill="'+color+'" opacity=".86"/>';
  s+='<path data-anatomy="knee-fold" d="M '+n(leg.knee.x-knee*.14)+' '+n(leg.knee.y+1)+' Q '+n(leg.knee.x)+' '+n(leg.knee.y+2.8)+' '+n(leg.knee.x+knee*.14)+' '+n(leg.knee.y+1)+'" fill="none" stroke="#222E3E" stroke-width="1" stroke-linecap="round" opacity=".48"/>';
  s+='<path d="M '+n(leg.knee.x-knee*.09)+' '+n(leg.knee.y-2)+' Q '+n(leg.knee.x)+' '+n(leg.knee.y-2.7)+' '+n(leg.knee.x+knee*.08)+' '+n(leg.knee.y-1.9)+'" fill="none" stroke="#D5DCE3" stroke-width=".8" stroke-linecap="round" opacity=".46"/>';
  s+='<path data-anatomy="ankle-cuff" d="M '+n(leg.ankle.x-ankle*.34)+' '+n(leg.ankle.y-4)+' Q '+n(leg.ankle.x)+' '+n(leg.ankle.y-1)+' '+n(leg.ankle.x+ankle*.34)+' '+n(leg.ankle.y-4)+'" fill="none" stroke="#1F2C3B" stroke-width="1.1" stroke-linecap="round" opacity=".7"/>';
  s+='<g data-anatomy="shoe" transform="translate('+n(foot.x)+' '+n(foot.y-2)+') rotate('+n(deg(foot.angle||0))+') scale('+(near?"1":"0.92")+' 1)">';
  s+='<path d="M -13 -7 Q -10 -10 -5 -8 L 5 -6 Q 11 -5 15 0 Q 20 3 16 6 Q 12 8 5 7 L -9 6 Q -16 5 -14 -1 Z" fill="#202A3A" stroke="#202A3A" stroke-width="1.8" stroke-linejoin="round"/>';
  s+='<path d="M -9 -6 Q -6 -8 -2 -5 L 6 -3 Q 11 -1 12 2 L -10 2 Z" fill="'+c.shoe+'" stroke="#151E2C" stroke-width="1.1" stroke-linejoin="round"/>';
  s+='<path d="M -12 4 Q 0 6 15 4" stroke="#E9E7DE" stroke-width="1.8" stroke-linecap="round"/><path d="M -5 -3 L 2 -1" stroke="#AAB4C0" stroke-width="1.1" stroke-linecap="round" opacity=".7"/><path d="M -2 -2 L 1 0 M 1 -3 L 4 -1" stroke="#B7C1CC" stroke-width=".8" stroke-linecap="round" opacity=".75"/></g>';
  return s+'</g>';
}
function handSvg(arm,scene,mode,near,activity,pose) {
  const w=arm.wrist,e=arm.elbow,c=scene.character,state=pose?.activityState||{};
  const armAngle=Math.atan2(w.y-e.y,w.x-e.x);
  const shoulderAngle=Math.atan2(w.y-arm.shoulder.y,w.x-arm.shoulder.x);
  const angleDelta=(a,b)=>Math.atan2(Math.sin(a-b),Math.cos(a-b));
  const boundedAngle=(angle,reference,limit)=>reference+Math.max(-limit,Math.min(limit,angleDelta(angle,reference)));
  const gripWeight=state.pickupGripWeight||0;
  let handPose=mode==="carry"?"grip":"relaxed";
  if(activity==="reach"&&near) handPose=state.reachTarget?.active?"press":"point";
  else if(activity==="pick-up"&&near) handPose=gripWeight>=0.30?"grip":((state.pickupReachWeight||0)>=0.22?"point":"relaxed");
  let preferredAngle=armAngle,angleLimit=0.45,handOrientation="forearm-following";
  if(handPose==="relaxed") {
    // In screen-space SVG, local +X is the finger axis. Keep relaxed fingers
    // gravity-down in BOTH depth layers; mirroring local Y flips the thumb/palm.
    preferredAngle=Math.PI/2;
    angleLimit=0.56;
    handOrientation="gravity-down";
  } else if(handPose==="point"||handPose==="press") {
    let target=null;
    if(activity==="reach"&&state.reachTarget) target=state.reachTarget;
    else if(activity==="pick-up"&&state.pickupItem) {
      const anchor=state.pickupItem.graspAnchor||state.pickupItem;
      target={x:anchor.x,y:anchor.y};
    }
    preferredAngle=target?Math.atan2(target.y-arm.shoulder.y,target.x-arm.shoulder.x):shoulderAngle;
    angleLimit=0.40;
    handOrientation="target-directed";
  } else {
    let target=null;
    if(activity==="pick-up"&&state.pickupItem) target={x:state.pickupItem.x,y:state.pickupItem.y};
    else if(pose?.basket?.center) target=pose.basket.center;
    if(target) {
      preferredAngle=Math.atan2(target.y-w.y,target.x-w.x);
      handOrientation="object-directed";
    }
    angleLimit=0.78;
  }
  const angle=boundedAngle(armAngle,preferredAngle,angleLimit);
  const handScale=near?1:0.94;
  let s='<g data-anatomy="hand" data-hand-side="'+(near?"near":"far")+'" data-hand-pose="'+handPose+'" data-hand-orientation="'+handOrientation+'" data-hand-mirror="none" data-hand-angle-degrees="'+n(deg(angle))+'" data-grip="'+(handPose==="grip"?"grip":"relaxed")+'" transform="translate('+n(w.x)+' '+n(w.y)+') rotate('+n(deg(angle))+') scale('+handScale+' '+handScale+')" opacity="'+(near?1:0.88)+'">';
  if(handPose==="point"||handPose==="press") {
    const tip=handPose==="point"?23:17;
    s+='<path data-anatomy="palm" d="M -5 -3.8 Q -5 -7 -.5 -7.3 L 4.5 -6.4 Q 7 -5.7 7.8 -4.2 L '+(tip-2)+' -4.1 Q '+tip+' -4.1 '+tip+' -1.8 Q '+tip+' .1 '+(tip-2)+' .1 L 9 .1 Q 12 1.1 10.8 3.4 Q 10 5.5 7.1 4.7 L 3.8 3.4 Q 1.7 6.1 -.5 4.7 L -3 2.7 Q -6 1.4 -5 -3.8 Z" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.35" stroke-linejoin="round"/>';
    s+='<path data-anatomy="index-finger" d="M 6.5 -4.2 L '+(tip-1)+' -4.2" fill="none" stroke="#F6D0B1" stroke-width="1.0" stroke-linecap="round" opacity=".95"/>';
    s+='<path data-anatomy="finger-detail" d="M 5.2 -.9 Q 8 -2.1 10.7 -.2 M 4.1 1.2 Q 6.8 .4 8.7 2.4" fill="none" stroke="#925F49" stroke-width="1.0" stroke-linecap="round"/>';
    s+='<path data-anatomy="thumb-fold" d="M -1.7 -2.2 Q .2 .1 3.3 .5" fill="none" stroke="#925F49" stroke-width="1.15" stroke-linecap="round"/>';
  } else if(handPose==="grip") {
    s+='<path data-anatomy="palm" d="M -5 -3.8 Q -5 -7.1 -.8 -7.4 L 3.5 -6.5 Q 6.4 -6.1 7.7 -3.2 Q 10.3 -4.9 13.1 -3.2 Q 16.2 -1.5 14.6 1.1 Q 14.2 3.1 11.3 3.1 L 8.2 3.1 Q 10.1 5.1 7.5 7.1 Q 5.1 8.1 3.5 5.6 Q 1.7 7.2 -.1 5.1 L -2.5 3.2 Q -5.8 1.8 -5 -3.8 Z" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.35" stroke-linejoin="round"/>';
    s+='<path data-anatomy="finger-detail" d="M 4.7 -4.6 Q 8.5 -7.4 11.9 -4.8 Q 13.8 -3.4 12.5 -.7 M 5.8 -1.7 Q 9.5 -4.6 13.4 -1.9 Q 15.2 -.6 13.5 1.6 M 4.9 1.3 Q 8.7 -.6 11.2 2.2 Q 12.4 3.7 10.4 4.5" fill="none" stroke="#925F49" stroke-width="1.05" stroke-linecap="round"/>';
    s+='<path data-anatomy="thumb-fold" d="M -1.7 -2.2 Q .2 .1 3.3 .5 Q 5.3 .7 6.2 2.5" fill="none" stroke="#925F49" stroke-width="1.15" stroke-linecap="round"/>';
    s+='<path d="M -2.6 2.5 Q -.8 3.6 1 3.3" fill="none" stroke="#F6D0B1" stroke-width=".9" stroke-linecap="round" opacity=".85"/>';
  } else {
    s+='<path data-anatomy="palm" d="M -5 -3.8 Q -5 -7.1 -.8 -7.4 L 3.5 -6.5 Q 6.4 -6.1 7.7 -3.2 Q 10.3 -4.9 12.3 -2.9 Q 13.8 -1.1 12.2 .6 L 9.6 2.2 Q 10.7 4.5 8.0 6.4 Q 5.3 7.5 3.3 4.8 L -.3 3.4 Q -5.8 1.8 -5 -3.8 Z" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.35" stroke-linejoin="round"/>';
    s+='<path data-anatomy="finger-detail" d="M 5.2 -4.1 Q 8.1 -6.4 10.7 -4.1 M 5.3 -1.6 Q 8.3 -3.7 10.8 -1.6 M 4.6 .8 Q 7.2 -.1 9.1 1.7" fill="none" stroke="#925F49" stroke-width="1.0" stroke-linecap="round"/>';
    s+='<path d="M -2.7 -2.2 Q -.1 -.1 2 1" fill="none" stroke="#F6D0B1" stroke-width="1.0" stroke-linecap="round" opacity=".85"/>';
  }
  return s+'</g>';
}
function armSvg(arm,scene,sleeve,near,mode,activity,pose) {
  const c=scene.character;
  let s=organicLimb(arm.shoulder,arm.elbow,c.upper_arm_width_px||20,c.elbow_width_px||15,sleeve,"#203348",{midBulgeFactor:1.08});
  const dx=arm.elbow.x-arm.shoulder.x,dy=arm.elbow.y-arm.shoulder.y,len=Math.max(1e-6,Math.hypot(dx,dy)),nx=-dy/len,ny=dx/len;
  const cuff={x:arm.shoulder.x+dx*.78,y:arm.shoulder.y+dy*.78},half=(c.upper_arm_width_px||20)*.33;
  s+='<path data-anatomy="sleeve-cuff" d="M '+n(cuff.x+nx*half)+' '+n(cuff.y+ny*half)+' Q '+n(cuff.x)+' '+n(cuff.y)+' '+n(cuff.x-nx*half)+' '+n(cuff.y-ny*half)+'" fill="none" stroke="'+(c.shirt_shadow||"#285C78")+'" stroke-width="1.9" stroke-linecap="round"/>';
  s+=organicLimb(arm.elbow,arm.wrist,c.forearm_width_px||14,c.wrist_width_px||10,c.skin||"#E6B08A","#7B5544",{midBulgeFactor:1.12});
  s+='<ellipse data-anatomy="elbow" cx="'+n(arm.elbow.x)+'" cy="'+n(arm.elbow.y)+'" rx="2.8" ry="3.1" fill="'+c.skin+'" opacity=".92"/>';
  s+='<path data-anatomy="elbow-fold" d="M '+n(arm.elbow.x-2.6)+' '+n(arm.elbow.y+1.2)+' Q '+n(arm.elbow.x)+' '+n(arm.elbow.y+2.7)+' '+n(arm.elbow.x+2.6)+' '+n(arm.elbow.y+1.0)+'" fill="none" stroke="#925F49" stroke-width=".95" stroke-linecap="round" opacity=".56"/>';
  return s+handSvg(arm,scene,mode,near,activity,pose);
}
function frontHeadSvg(p,scene) {
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
function profileHeadSvg(p,scene) {
  const h=p.head,neck=p.neck,r=scene.character.head_radius_px,c=scene.character,rx=r*.91,ry=r*.94;
  let s='<g data-anatomy="head" data-contour="side-profile" data-face-design="soft-profile-v1" transform="rotate('+n(deg(p.headAngle))+' '+n(neck.x)+' '+n(neck.y)+')">';
  s+='<path data-profile-feature="silhouette" d="M '+n(h.x-rx*.28)+' '+n(h.y-ry*.96)+' C '+n(h.x+rx*.28)+' '+n(h.y-ry*1.04)+' '+n(h.x+rx*.77)+' '+n(h.y-ry*.76)+' '+n(h.x+rx*.82)+' '+n(h.y-ry*.39)+' C '+n(h.x+rx*.83)+' '+n(h.y-ry*.20)+' '+n(h.x+rx*.85)+' '+n(h.y-ry*.08)+' '+n(h.x+rx*.88)+' '+n(h.y-ry*.015)+' Q '+n(h.x+rx*.91)+' '+n(h.y+ry*.035)+' '+n(h.x+rx*.86)+' '+n(h.y+ry*.085)+' Q '+n(h.x+rx*.79)+' '+n(h.y+ry*.13)+' '+n(h.x+rx*.80)+' '+n(h.y+ry*.20)+' C '+n(h.x+rx*.82)+' '+n(h.y+ry*.29)+' '+n(h.x+rx*.72)+' '+n(h.y+ry*.37)+' '+n(h.x+rx*.63)+' '+n(h.y+ry*.42)+' C '+n(h.x+rx*.58)+' '+n(h.y+ry*.68)+' '+n(h.x+rx*.34)+' '+n(h.y+ry*.89)+' '+n(h.x+rx*.08)+' '+n(h.y+ry*.93)+' C '+n(h.x-rx*.36)+' '+n(h.y+ry*.98)+' '+n(h.x-rx*.86)+' '+n(h.y+ry*.68)+' '+n(h.x-rx*.97)+' '+n(h.y+ry*.22)+' C '+n(h.x-rx*1.05)+' '+n(h.y-ry*.24)+' '+n(h.x-rx*.78)+' '+n(h.y-ry*.79)+' '+n(h.x-rx*.28)+' '+n(h.y-ry*.96)+' Z" fill="'+c.skin+'" stroke="#704A3B" stroke-width="1.55" stroke-linejoin="round"/>';
  s+='<path data-profile-feature="hair" d="M '+n(h.x-rx*.96)+' '+n(h.y+ry*.06)+' C '+n(h.x-rx*1.02)+' '+n(h.y-ry*.43)+' '+n(h.x-rx*.61)+' '+n(h.y-ry*.99)+' '+n(h.x-rx*.13)+' '+n(h.y-ry*.98)+' C '+n(h.x+rx*.36)+' '+n(h.y-ry*1.02)+' '+n(h.x+rx*.77)+' '+n(h.y-ry*.72)+' '+n(h.x+rx*.83)+' '+n(h.y-ry*.36)+' C '+n(h.x+rx*.58)+' '+n(h.y-ry*.55)+' '+n(h.x+rx*.25)+' '+n(h.y-ry*.60)+' '+n(h.x-rx*.04)+' '+n(h.y-ry*.42)+' C '+n(h.x-rx*.25)+' '+n(h.y-ry*.27)+' '+n(h.x-rx*.57)+' '+n(h.y-ry*.19)+' '+n(h.x-rx*.66)+' '+n(h.y+ry*.12)+' Z" fill="'+c.hair+'"/>';
  s+='<ellipse data-profile-feature="ear" cx="'+n(h.x-rx*.62)+'" cy="'+n(h.y+ry*.12)+'" rx="2.8" ry="3.7" fill="'+c.skin+'" stroke="#8C604B" stroke-width="1.0"/>';
  s+='<path data-profile-feature="brow" d="M '+n(h.x+rx*.30)+' '+n(h.y-ry*.18)+' Q '+n(h.x+rx*.48)+' '+n(h.y-ry*.25)+' '+n(h.x+rx*.62)+' '+n(h.y-ry*.16)+'" fill="none" stroke="#543C32" stroke-width="1.05" stroke-linecap="round"/>';
  const eyeX = h.x + rx * .50, eyeY = h.y - ry * .07;
  const gazeX = Math.max(-1.25, Math.min(1.25, p.activityState?.gazeOffsetX || 0));
  const gazeY = Math.max(-.75, Math.min(.75, p.activityState?.gazeOffsetY || 0));
  s+='<ellipse data-profile-feature="eye" cx="'+n(eyeX)+'" cy="'+n(eyeY)+'" rx="2.6" ry="2.2" fill="#FFF7E9" stroke="#543C32" stroke-width=".75"/>';
  s+='<circle data-profile-feature="pupil" cx="'+n(eyeX+gazeX)+'" cy="'+n(eyeY+gazeY)+'" r="1.25" fill="#252A31"/>';
  s+='<circle cx="'+n(eyeX+gazeX-.38)+'" cy="'+n(eyeY+gazeY-.42)+'" r=".35" fill="#FFFDF6"/>';
  s+='<path data-profile-feature="nose" d="M '+n(h.x+rx*.75)+' '+n(h.y-ry*.01)+' Q '+n(h.x+rx*.86)+' '+n(h.y+ry*.055)+' '+n(h.x+rx*.81)+' '+n(h.y+ry*.12)+'" fill="none" stroke="#8A5B48" stroke-width=".95" stroke-linecap="round" stroke-linejoin="round"/>';
  s+='<path data-profile-feature="mouth" d="M '+n(h.x+rx*.60)+' '+n(h.y+ry*.44)+' Q '+n(h.x+rx*.72)+' '+n(h.y+ry*.455)+' '+n(h.x+rx*.84)+' '+n(h.y+ry*.44)+'" fill="none" stroke="#8D5144" stroke-width="1.0" stroke-linecap="round"/>';
  return s+'</g>';
}
function headSvg(p,scene) {
  return (scene.character.view_mode||"profile-right")==="profile-right" ? profileHeadSvg(p,scene) : frontHeadSvg(p,scene);
}
function neckSvg(p,scene) {
  const c=scene.character,top=p.neck,bottom={x:p.chest.x,y:p.chest.y-2};
  return '<path data-anatomy="neck" d="M '+n(top.x-5)+' '+n(top.y)+' Q '+n(top.x)+' '+n(top.y-1)+' '+n(top.x+5)+' '+n(top.y)+' L '+n(bottom.x+8)+' '+n(bottom.y)+' Q '+n(bottom.x)+' '+n(bottom.y+5)+' '+n(bottom.x-8)+' '+n(bottom.y)+' Z" fill="'+c.skin+'" stroke="#7B5544" stroke-width="1.6" stroke-linejoin="round"/>'+
    '<path data-anatomy="collar" d="M '+n(bottom.x-11)+' '+n(bottom.y+2)+' Q '+n(bottom.x)+' '+n(bottom.y+10)+' '+n(bottom.x+11)+' '+n(bottom.y+2)+'" fill="none" stroke="#203348" stroke-width="2.6" stroke-linecap="round"/>';
}
function activityEnvironmentSvg(p, scene, activity) {
  const floor = scene.background.horizon_y;
  let s = "";
  if (activity === "sit-to-stand" && p.activityState?.chair) {
    const chair = p.activityState.chair, x = chair.x, y = chair.seatY;
    s += '<g data-environment="chair" stroke="#4A5564" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round">';
    s += '<rect x="'+n(x-36)+'" y="'+n(y-53)+'" width="13" height="52" rx="3" fill="#B7C0CA"/>';
    s += '<rect x="'+n(x-32)+'" y="'+n(y-4)+'" width="68" height="9" rx="3" fill="#9EAAB7"/>';
    s += '<path d="M '+n(x-24)+' '+n(y+3)+' L '+n(x-27)+' '+n(floor-2)+' M '+n(x+27)+' '+n(y+3)+' L '+n(x+30)+' '+n(floor-2)+'" fill="none" stroke-width="4"/>';
    s += '<path d="M '+n(x-30)+' '+n(floor-2)+' L '+n(x-23)+' '+n(floor-2)+' M '+n(x+26)+' '+n(floor-2)+' L '+n(x+33)+' '+n(floor-2)+'" fill="none" stroke-width="3"/>';
    s += '</g>';
  }
  if (activity === "reach" && p.activityState?.reachTarget) {
    const target = p.activityState.reachTarget, x = target.x, y = target.y;
    s += '<g data-environment="reach-target" data-button-state="'+(target.active ? "pressed" : "idle")+'" stroke="#566273" stroke-linejoin="round" stroke-linecap="round">';
    s += '<path d="M '+n(x)+' '+n(y+20)+' L '+n(x)+' '+n(floor-2)+'" fill="none" stroke-width="5"/>';
    s += '<rect x="'+n(x-16)+'" y="'+n(y-22)+'" width="32" height="44" rx="5" fill="#E8E2D4" stroke-width="2.3"/>';
    s += '<rect x="'+n(x-11)+'" y="'+n(y-17)+'" width="22" height="34" rx="3" fill="#F8F4E9" stroke="#9CA6AE" stroke-width="1.1"/>';
    if (target.active) s += '<circle data-button-feedback="press-ring" cx="'+n(x)+'" cy="'+n(y)+'" r="14" fill="none" stroke="#E8A15C" stroke-width="2.4" opacity=".85"/>';
    s += '<circle cx="'+n(x)+'" cy="'+n(y)+'" r="'+n(target.active ? target.radius * 0.72 : target.radius)+'" fill="'+(target.active ? "#8E3D32" : "#C45B43")+'" stroke="#713F36" stroke-width="2.2"/>';
    s += '<circle cx="'+n(x)+'" cy="'+n(y)+'" r="3.2" fill="#F9D9AC" stroke="none"/>';
    s += '</g>';
  }
  if (activity === "pick-up" && p.activityState?.pickupItem) {
    const item = p.activityState.pickupItem;
    s += '<g data-environment="pickup-table" fill="none" stroke="#566273" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">';
    s += '<rect x="'+n(item.tableX-37)+'" y="'+n(item.tableTopY-4)+'" width="69" height="8" rx="2" fill="#AEB7C1" stroke="#566273" stroke-width="2"/>';
    s += '<path d="M '+n(item.tableX-30)+' '+n(item.tableTopY+3)+' L '+n(item.tableX-30)+' '+n(floor-2)+' M '+n(item.tableX+25)+' '+n(item.tableTopY+3)+' L '+n(item.tableX+25)+' '+n(floor-2)+'" fill="none" stroke-width="4"/>';
    s += '</g>';
  }
  return s;
}
function pickupItemSvg(item) {
  if (!item) return "";
  const x = item.x, y = item.y;
  return '<g data-prop="pickup-item" data-held="'+String(item.held)+'" data-grip-weight="'+n(item.gripWeight)+'" transform="translate('+n(x)+' '+n(y)+')">' +
    '<path d="M -17 -8 L -10 -13 L 15 -11 L 17 7 L 6 13 L -17 8 Z" fill="#C58B51" stroke="#6F492B" stroke-width="1.8" stroke-linejoin="round"/>' +
    '<path d="M -10 -13 L -8 4 L 17 7 M -8 4 L 6 13" fill="none" stroke="#E5BB83" stroke-width="1.7"/>' +
    '<path d="M -2 -12 L 1 11" stroke="#8D5E35" stroke-width="2.4" opacity=".72"/>' +
    '</g>';
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
export function renderSvgFrame(scene,frameIndex,armMode,activity="walk") {
  const mode=armMode||scene.motion.arm_mode||"carry";
  if(mode!=="carry"&&mode!=="free") throw new RangeError("Unsupported render arm mode.");
  const p=activity==="walk"?evaluateLocomotion(scene,frameIndex,mode):evaluateActivity(scene,frameIndex,activity,mode),floor=scene.background.horizon_y,c=scene.character;
  let s='<?xml version="1.0" encoding="UTF-8"?><svg xmlns="http://www.w3.org/2000/svg" width="'+scene.canvas.width+'" height="'+scene.canvas.height+'" viewBox="0 0 '+scene.canvas.width+' '+scene.canvas.height+'" role="img" data-view="'+(c.view_mode||"profile-right")+'" data-activity="'+activity+'">';
  s+='<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#FBFAF3"/><stop offset="1" stop-color="'+scene.background.color+'"/></linearGradient></defs>';
  s+='<rect width="100%" height="100%" fill="url(#sky)"/><circle cx="1080" cy="140" r="74" fill="#E5E2D6" opacity=".35"/>';
  s+='<path d="M 0 '+n(floor)+' L '+scene.canvas.width+' '+n(floor)+' L '+scene.canvas.width+' '+scene.canvas.height+' L 0 '+scene.canvas.height+' Z" fill="'+scene.background.floor+'"/>';
  s+='<path d="M 0 '+n(floor)+' L '+scene.canvas.width+' '+n(floor)+'" stroke="#C7C0B0" stroke-width="2"/>';
  for(let i=0;i<11;i++){const x=i*145+22;s+='<path d="M '+x+' '+(floor+24)+' L '+(x+70)+' '+(floor+24)+'" stroke="#D8D2C3" stroke-width="1"/>';}
  if(activity!=="walk") s+='<g data-activity-overlay="label"><text x="'+(scene.canvas.width-36)+'" y="48" text-anchor="end" font-family="Inter,Arial,sans-serif" font-size="17" font-weight="750" fill="#203348" letter-spacing="0.7">'+(ACTIVITY_LABELS[activity]||activity.toUpperCase())+'</text></g>';
  // Activity proof clips use close action framing; keep the floor and HUD stable in screen space.
  // Center the actor horizontally and anchor the zoom at the floor contact plane so planted feet
  // remain visually grounded while the pose/prop interaction becomes readable at normal playback size.
  if (activity !== "walk") {
    const cameraScale = 1.5;
    // Anchor the action camera to the initial root, not the animated pelvis.
    // Tracking the pelvis every frame erased visible horizontal root/weight
    // transfer and made a moving camera compensate for the character's motion.
    const cameraAnchorX = Number.isFinite(scene.motion.start_x) ? scene.motion.start_x : p.pelvis.x;
    const translateX = scene.canvas.width * 0.42 - cameraScale * cameraAnchorX;
    const translateY = floor * (1 - cameraScale);
    s += '<g data-camera-framing="close-action" data-camera-anchor="static-root-start" transform="translate('+n(translateX)+' '+n(translateY)+') scale('+cameraScale+')">';
  }
  s += activityEnvironmentSvg(p, scene, activity);
  s+='<g id="characterRig" data-rig-frame="'+frameIndex+'">';
  s+='<ellipse cx="'+n(p.pelvis.x+12)+'" cy="'+n(floor+5)+'" rx="63" ry="9" fill="#9C988B" opacity=".22"/>';
  s+=legSvg(p.rightLeg,p.rightFoot,scene,false)+legSvg(p.leftLeg,p.leftFoot,scene,true);
  s+=armSvg(p.farArm,scene,"#2F6D8D",false,mode,activity,p);
  const pel=p.pelvis,chest=p.chest,near=p.shoulders.near,far=p.shoulders.far;
  const profile=(c.view_mode||"profile-right")==="profile-right";
  if(profile){
    const bodyHalf=c.profile_torso_half_width_px||15,hipHalf=c.profile_hip_half_width_px||10;
    // Express the contour in the chest-to-pelvis spine frame. This is required for
    // the shirt silhouette to follow a forward lean rather than staying screen-vertical.
    const dx=pel.x-chest.x,dy=pel.y-chest.y,bodyLen=Math.max(1e-6,Math.hypot(dx,dy));
    const nx=dy/bodyLen,ny=-dx/bodyLen;
    const P=(t,side,width)=>({x:chest.x+dx*t+nx*side*width,y:chest.y+dy*t+ny*side*width});
    const xy=q=>n(q.x)+' '+n(q.y);
    const topR=P(.05,1,bodyHalf*.68),upperR=P(.24,1,bodyHalf),midR=P(.51,1,bodyHalf*.86),waistR=P(.78,1,bodyHalf*.66),hipR=P(.94,1,hipHalf),lowR=P(1,1,hipHalf*.60);
    const topL=P(.05,-1,bodyHalf*.68),upperL=P(.24,-1,bodyHalf),midL=P(.51,-1,bodyHalf*.86),waistL=P(.78,-1,bodyHalf*.66),hipL=P(.94,-1,hipHalf),lowL=P(1,-1,hipHalf*.60);
    const d=[
      'M '+xy(topR),
      'C '+xy(P(.12,1,bodyHalf*.98))+' '+xy(P(.17,1,bodyHalf))+' '+xy(upperR),
      'C '+xy(P(.37,1,bodyHalf*.96))+' '+xy(P(.43,1,bodyHalf*.89))+' '+xy(midR),
      'C '+xy(P(.63,1,bodyHalf*.82))+' '+xy(P(.70,1,bodyHalf*.72))+' '+xy(waistR),
      'L '+xy(hipR),
      'Q '+xy(P(.985,1,hipHalf*.82))+' '+xy(lowR),
      'Q '+xy(P(1.045,0,0))+' '+xy(lowL),
      'Q '+xy(P(.985,-1,hipHalf*.82))+' '+xy(hipL),
      'L '+xy(waistL),
      'C '+xy(P(.70,-1,bodyHalf*.72))+' '+xy(P(.63,-1,bodyHalf*.82))+' '+xy(midL),
      'C '+xy(P(.43,-1,bodyHalf*.89))+' '+xy(P(.37,-1,bodyHalf*.96))+' '+xy(upperL),
      'C '+xy(P(.17,-1,bodyHalf))+' '+xy(P(.12,-1,bodyHalf*.98))+' '+xy(topL),
      'Q '+xy(P(0,0,0))+' '+xy(topR)+' Z'
    ].join(' ');
    s+='<path data-anatomy="torso" data-contour="side-profile" data-contour-frame="spine-aligned" d="'+d+'" fill="'+c.shirt+'" stroke="#203348" stroke-width="2.7" stroke-linejoin="round"/>';
    const seamA=P(.17,-1,bodyHalf*.28),seamB=P(.46,-1,bodyHalf*.25),seamC=P(.70,-1,bodyHalf*.16);
    const seamControl=P(.31,-1,bodyHalf*.26);
    s+='<path data-torso-detail="seam" d="M '+xy(seamA)+' Q '+xy(seamControl)+' '+xy(seamB)+' L '+xy(seamC)+'" fill="none" stroke="'+c.shirt_shadow+'" stroke-width="1.8" stroke-linecap="round" opacity=".9"/>';
    const wb1=P(.965,-1,hipHalf*.78),wb2=P(.965,1,hipHalf*.78),wbm=P(1,0,0);
    s+='<path data-anatomy="waistband" data-contour="side-profile" data-contour-frame="spine-aligned" d="M '+xy(wb1)+' Q '+xy(wbm)+' '+xy(wb2)+'" fill="none" stroke="#263347" stroke-width="2.2"/>';
  }else{
  const sh=c.shoulder_half_width_px||23,hip=c.pelvis_half_width_px||22;
  s+='<path data-anatomy="torso" d="M '+n(chest.x-sh-8)+' '+n(chest.y+7)+' Q '+n(chest.x-sh-14)+' '+n(chest.y+20)+' '+n(chest.x-22)+' '+n(chest.y+42)+' L '+n(chest.x-17)+' '+n(pel.y-6)+' Q '+n(pel.x-hip*.65)+' '+n(pel.y+6)+' '+n(pel.x-hip)+' '+n(pel.y+5)+' Q '+n(pel.x)+' '+n(pel.y+15)+' '+n(pel.x+hip)+' '+n(pel.y+5)+' Q '+n(pel.x+hip*.65)+' '+n(pel.y+6)+' '+n(chest.x+17)+' '+n(pel.y-6)+' L '+n(chest.x+22)+' '+n(chest.y+42)+' Q '+n(chest.x+sh+14)+' '+n(chest.y+20)+' '+n(chest.x+sh+8)+' '+n(chest.y+7)+' Q '+n(chest.x+sh*.45)+' '+n(chest.y-5)+' '+n(chest.x)+' '+n(chest.y-4)+' Q '+n(chest.x-sh*.45)+' '+n(chest.y-5)+' '+n(chest.x-sh-8)+' '+n(chest.y+7)+' Z" fill="'+c.shirt+'" stroke="#203348" stroke-width="2.7" stroke-linejoin="round"/>';
  s+='<path d="M '+n(chest.x-14)+' '+n(chest.y+13)+' Q '+n(chest.x)+' '+n(chest.y+21)+' '+n(chest.x+14)+' '+n(chest.y+13)+'" fill="none" stroke="'+c.shirt_shadow+'" stroke-width="2.3" stroke-linecap="round" opacity=".9"/>';
  s+='<path d="M '+n(chest.x-5)+' '+n(chest.y+24)+' Q '+n(chest.x-1)+' '+n(chest.y+40)+' '+n(chest.x-4)+' '+n(chest.y+53)+'" fill="none" stroke="#DCE9EC" stroke-width="1.3" opacity=".22"/>';
  s+='<path data-anatomy="waistband" d="M '+n(pel.x-hip)+' '+n(pel.y+6)+' Q '+n(pel.x)+' '+n(pel.y+13)+' '+n(pel.x+hip)+' '+n(pel.y+6)+'" fill="none" stroke="#263347" stroke-width="2.6"/>';
  }
  s+=neckSvg(p,scene);
  s+=headSvg(p,scene);
  if (activity === "pick-up") s += pickupItemSvg(p.activityState.pickupItem);
  if(mode==="carry") s+=basketSvg(p,scene);
  s+=armSvg(p.nearArm,scene,"#3A82A3",true,mode,activity,p);
  s+='</g><!--CHARACTER-RIG-END-->';
  if (activity !== "walk") s += '</g><!--ACTIVITY-CAMERA-END-->';
  s+='<rect x="34" y="28" width="388" height="82" rx="14" fill="#FFFEFA" opacity=".92" stroke="#DAD5C7"/>';
  s+='<text x="54" y="57" font-family="DejaVu Sans,sans-serif" font-size="18" font-weight="700" fill="#243345">MOTION STUDIO / v0.9.5</text>';
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
    maxFootStepPx: Math.max(pointSteps.leftFoot, pointSteps.rightFoot),
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
    sideProfileDiagnostics: {
      viewMode: c.view_mode || "front",
      nearFarLegCenterGapPx: 2 * (c.leg_depth_projection_px || 0),
      nearFarShoulderCenterGapPx: 2 * (c.shoulder_depth_projection_px || 0),
      torsoHalfWidthPx: c.profile_torso_half_width_px ?? null,
      hipHalfWidthPx: c.profile_hip_half_width_px ?? null,
      farToNearThighWidthRatio: c.far_thigh_width_px && c.thigh_width_px ? c.far_thigh_width_px / c.thigh_width_px : null,
      farToNearKneeWidthRatio: c.far_knee_width_px && c.knee_width_px ? c.far_knee_width_px / c.knee_width_px : null
    },
    motionEnvelopeDiagnostics: {
      cycleSeconds: m.cycle_seconds,
      cadenceStepsPerMinute: 120 / m.cycle_seconds,
      startRampSeconds: m.start_ramp_seconds || 0,
      stopRampSeconds: m.stop_ramp_seconds || 0,
      cycleLiftVariationFraction: m.cycle_lift_variation_fraction || 0,
      cycleArmVariationFraction: m.cycle_arm_variation_fraction || 0,
      contactCompressionPx: m.contact_compression_px || 0,
      contactTorsoReactionDegrees: (m.contact_torso_reaction_radians || 0) * 180 / Math.PI,
      strideLengthPx: m.stride_length_px * (m.screen_stride_scale || 1),
      swingLiftPx: m.swing_lift_px,
      freeArmSwingAmplitudePx: m.free_arm_swing_px,
      freeArmVerticalAmplitudePx: m.free_arm_vertical_swing_px || 0,
      torsoSwayPeakDegrees: ((Math.abs(m.torso_sway_radians) + Math.abs(m.secondary_torso_sway_radians || 0)) * 180 / Math.PI),
      headFollowRadians: m.head_follow_radians || 0,
      headBobRadians: m.head_bob_radians || 0,
      basketVerticalResponsePx: m.basket_vertical_response_px,
      basketTiltPeakDegrees: Math.abs(m.basket_tilt_radians || 0) * 180 / Math.PI
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
  const manifest={schemaVersion:"1.7.0",generator:"Motion Studio v0.9.5 damped-human-gait SVG preview",producedAt:"deterministic-build",scenes:results.map(x=>x.summary),productionStatus:"prototype",visualReviewRequired:true};
  fs.writeFileSync(path.join(out,"render-manifest.json"),JSON.stringify(manifest,null,2)+"\n","utf8");
  process.stdout.write(JSON.stringify({outputDir:out,scenes:manifest.scenes.map(x=>({mode:x.armMode,frames:x.frameCount,durationSeconds:x.durationSeconds,finite:x.allPoseValuesFinite}))},null,2)+"\n");
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) run();
