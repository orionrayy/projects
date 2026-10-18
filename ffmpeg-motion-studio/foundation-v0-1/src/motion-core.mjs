import {evaluateAction} from "./action-model.mjs";
import {evaluatePoseQuality} from "./pose-quality.mjs";
export function clamp(v,lo,hi){return Math.min(hi,Math.max(lo,v));}
export function lerp(a,b,t){return a+(b-a)*t;}
export function smoothstep(t){const u=clamp(t,0,1);return u*u*(3-2*u);}
export function distance(a,b){return Math.hypot(b.x-a.x,b.y-a.y);}
function candidate(shoulder,angle,length){return {x:shoulder.x+length*Math.cos(angle),y:shoulder.y+length*Math.sin(angle)};}
export function solveTwoBoneIK(shoulder,requestedWrist,upperLength,lowerLength,bend=1,poleTarget=null){
 if(!(upperLength>0&&lowerLength>0))throw new RangeError("IK lengths must be positive.");
 const dx=requestedWrist.x-shoulder.x,dy=requestedWrist.y-shoulder.y,rawDistance=Math.hypot(dx,dy);
 const minReach=Math.abs(upperLength-lowerLength)+1e-6,maxReach=upperLength+lowerLength-1e-6;
 const d=clamp(rawDistance,minReach,maxReach),a=rawDistance<1e-8?0:Math.atan2(dy,dx);
 const wrist={x:shoulder.x+Math.cos(a)*d,y:shoulder.y+Math.sin(a)*d};
 const cosine=clamp((upperLength*upperLength+d*d-lowerLength*lowerLength)/(2*upperLength*d),-1,1);
 const offset=Math.acos(cosine),ca=candidate(shoulder,a+offset,upperLength),cb=candidate(shoulder,a-offset,upperLength);
 const elbow=poleTarget?(distance(ca,poleTarget)<=distance(cb,poleTarget)?ca:cb):(bend>=0?ca:cb);
 return {shoulder:{...shoulder},elbow,wrist,requestedWrist:{...requestedWrist},requestedDistance:rawDistance,actualDistance:d,
  reachable:Math.abs(rawDistance-d)<.02,upperError:Math.abs(distance(shoulder,elbow)-upperLength),lowerError:Math.abs(distance(elbow,wrist)-lowerLength)};
}
export function evaluateFrame(scene,frameIndex){
 if(!Number.isInteger(frameIndex))throw new TypeError("frameIndex must be an integer.");
 if(frameIndex<0||frameIndex>=scene.duration_frames)throw new RangeError("frameIndex outside declared timeline.");
 const action=evaluateAction(scene,frameIndex),c=scene.character,ik=solveTwoBoneIK(
  action.rig.shoulder,action.requestedWrist,c.upper_arm_length,c.forearm_length,scene.motion.elbow_bend,action.elbowPole);
 const handAngle=Math.atan2(action.target.y-ik.wrist.y,action.target.x-ik.wrist.x);
 const fingerTip={x:ik.wrist.x+Math.cos(handAngle)*c.hand_length,y:ik.wrist.y+Math.sin(handAngle)*c.hand_length};
 const diagnostics={reachable:ik.reachable,requestedReachPx:ik.requestedDistance,maxReachPx:c.upper_arm_length+c.forearm_length,
  upperSegmentErrorPx:ik.upperError,lowerSegmentErrorPx:ik.lowerError,requestedTargetErrorPx:distance(ik.wrist,action.requestedWrist),
  targetErrorPx:distance(fingerTip,action.target),settleAmplitudeUsedPx:action.settleAmplitudeUsedPx};
 const state={frameIndex,timeSeconds:action.timeSeconds,phase:action.phase,root:action.rig.root,head:action.rig.head,
  headAngle:action.rig.headAngle,torsoAngle:action.rig.torsoAngle,neckBase:action.rig.neckBase,neckTop:action.rig.neckTop,
  shoulder:action.rig.shoulder,elbow:ik.elbow,wrist:ik.wrist,requestedWrist:action.requestedWrist,fingerTip,handAngle,
  forearmAngle:Math.atan2(ik.wrist.y-ik.elbow.y,ik.wrist.x-ik.elbow.x),pelvis:action.rig.pelvis,target:action.target,diagnostics,
  action:{reachProgress:action.reachProgress,anticipationWeight:action.anticipationWeight,settleTime:action.settleTime,
   holdTime:action.holdTime,contactWrist:action.contactWrist,restWrist:action.restWrist,elbowPole:action.elbowPole}};
 state.quality=evaluatePoseQuality(scene,state);
 diagnostics.handAimErrorDegrees=state.quality.handAimErrorDegrees;
 diagnostics.poseQualityPassed=state.quality.passed;
 return state;
}
