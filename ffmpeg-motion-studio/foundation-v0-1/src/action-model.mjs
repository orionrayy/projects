import {createCharacterRig,suggestElbowPole} from "./character-rig.mjs";
const clamp=(v,a,b)=>Math.min(b,Math.max(a,v));
const smoothstep=t=>{const u=clamp(t,0,1);return u*u*(3-2*u);};
const bezier=(a,b,c,d,t)=>{const u=1-t,A=u*u*u,B=3*u*u*t,C=3*u*t*t,D=t*t*t;return {x:A*a.x+B*b.x+C*c.x+D*d.x,y:A*a.y+B*b.y+C*c.y+D*d.y};};
const unit=(a,b)=>{const x=b.x-a.x,y=b.y-a.y,d=Math.max(1e-8,Math.hypot(x,y));return {x:x/d,y:y/d};};
export function evaluateAction(scene,frameIndex) {
 const c=scene.character,m=scene.motion,o=c.origin,t=frameIndex/scene.fps;
 const aEnd=m.anticipation_seconds,rEnd=aEnd+m.reach_seconds,sDuration=m.settle_seconds??.7;
 const sTime=Math.max(0,t-rEnd),holdTime=Math.max(0,sTime-sDuration);
 const aP=aEnd>0?clamp(t/aEnd,0,1):1,aW=aEnd>0?Math.sin(Math.PI*aP):0;
 const rLinear=clamp((t-aEnd)/m.reach_seconds,0,1),rP=smoothstep(rLinear);
 const pre=t<aEnd,reach=t>=aEnd&&t<rEnd,settle=t>=rEnd&&sTime<sDuration;
 const phase=pre?"anticipate":reach?"reach":settle?"settle":"hold";
 let torsoAngle;
 if(pre) torsoAngle=-.026*aW;
 else if(reach) torsoAngle=.044*rP;
 else torsoAngle=.012+.032*Math.exp(-m.settle_decay*sTime)*Math.cos(8*sTime)+.0025*Math.sin(2*Math.PI*.72*holdTime);
 const rootShift=pre?-m.anticipation_px*aW:1.8*rP*Math.exp(-4*sTime);
 const rig=createCharacterRig(scene,{rootX:o.x+rootShift,torsoAngle,headNod:-.012*aW+.014*rP+.002*Math.sin(2*Math.PI*.72*holdTime)});
 const target={x:scene.board.target_x,y:scene.board.target_y},direction=unit(rig.shoulder,target);
 const goal={x:target.x-direction.x*c.hand_length,y:target.y-direction.y*c.hand_length};
 const rest={x:rig.root.x+c.rest_pose.wrist_offset_x,y:rig.root.y+c.rest_pose.wrist_offset_y};
 let wrist,settleAmplitudeUsedPx=0;
 if(pre) wrist={x:rest.x-9*aW,y:rest.y-13*aW};
 else if(reach) {
   const dx=goal.x-rest.x,dy=goal.y-rest.y;
   wrist=bezier(rest,{x:rest.x+dx*.22,y:rest.y-28},{x:goal.x-dx*.18,y:goal.y-dy*.18},goal,rP);
 } else if(settle) {
   const decay=Math.exp(-m.settle_decay*sTime);settleAmplitudeUsedPx=m.settle_amplitude_px*decay;
   wrist={x:goal.x+settleAmplitudeUsedPx*Math.sin(m.settle_frequency*sTime),y:goal.y+settleAmplitudeUsedPx*.28*(1-Math.cos(m.settle_frequency*sTime))};
 } else wrist={...goal};
 const aim=unit(wrist,target),handAngle=Math.atan2(aim.y,aim.x);
 return {frameIndex,timeSeconds:t,phase,rig,target,requestedWrist:wrist,handAngle,
   elbowPole:suggestElbowPole(rig.shoulder,wrist,c.upper_arm_length,m.elbow_bend),
   settleAmplitudeUsedPx,anticipationWeight:aW,reachProgress:rP,settleTime:sTime,holdTime,
   contactWrist:goal,restWrist:rest};
}
