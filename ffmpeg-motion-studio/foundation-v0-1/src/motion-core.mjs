// Deterministic frame-index motion kernel; no random or accumulated playback state.
export function clamp(v,lo,hi){return Math.min(hi,Math.max(lo,v));}
export function lerp(a,b,t){return a+(b-a)*t;}
export function smoothstep(t){const u=clamp(t,0,1);return u*u*(3-2*u);}
export function distance(a,b){return Math.hypot(b.x-a.x,b.y-a.y);}
export function solveTwoBoneIK(shoulder,requestedWrist,upperLength,lowerLength,bend=1){
 if(!(upperLength>0&&lowerLength>0))throw new RangeError("IK lengths must be positive.");
 const dx=requestedWrist.x-shoulder.x,dy=requestedWrist.y-shoulder.y,raw=Math.hypot(dx,dy);
 const min=Math.abs(upperLength-lowerLength)+1e-6,max=upperLength+lowerLength-1e-6,d=clamp(raw,min,max),a=raw<1e-8?0:Math.atan2(dy,dx);
 const wrist={x:shoulder.x+Math.cos(a)*d,y:shoulder.y+Math.sin(a)*d};
 const cs=clamp((upperLength*upperLength+d*d-lowerLength*lowerLength)/(2*upperLength*d),-1,1),ea=a+Math.acos(cs)*(bend>=0?1:-1);
 const elbow={x:shoulder.x+upperLength*Math.cos(ea),y:shoulder.y+upperLength*Math.sin(ea)};
 return {shoulder:{...shoulder},elbow,wrist,requestedWrist:{...requestedWrist},requestedDistance:raw,actualDistance:d,reachable:Math.abs(raw-d)<.02,upperError:Math.abs(distance(shoulder,elbow)-upperLength),lowerError:Math.abs(distance(elbow,wrist)-lowerLength)};
}
export function evaluateFrame(scene,frameIndex){
 if(!Number.isInteger(frameIndex))throw new TypeError("frameIndex must be an integer.");
 if(frameIndex<0||frameIndex>=scene.duration_frames)throw new RangeError("frameIndex outside declared timeline.");
 const t=frameIndex/scene.fps,c=scene.character,m=scene.motion,b=scene.board,o=c.origin,ae=m.anticipation_seconds,re=ae+m.reach_seconds;
 const anticipation=m.anticipation_px*Math.sin(Math.PI*clamp(t/Math.max(ae,1e-8),0,1)),rootX=o.x-anticipation,shoulder={x:rootX+c.shoulder.offset_x,y:o.y+c.shoulder.offset_y};
 const idle={x:o.x+80-anticipation*.2,y:o.y+100},finalWrist={x:b.target_x-c.hand_length,y:b.target_y},p=smoothstep((t-ae)/m.reach_seconds);
 let desired={x:lerp(idle.x,finalWrist.x,p),y:lerp(idle.y,finalWrist.y,p)};
 if(t>re){const st=t-re,d=Math.exp(-m.settle_decay*st);desired={x:desired.x+m.settle_amplitude_px*d*Math.sin(m.settle_frequency*st),y:desired.y+m.settle_amplitude_px*.25*d*Math.cos(m.settle_frequency*st)};}
 const ik=solveTwoBoneIK(shoulder,desired,c.upper_arm_length,c.forearm_length,m.elbow_bend),tip={x:ik.wrist.x+c.hand_length,y:ik.wrist.y-1.5};
 return {frameIndex,timeSeconds:t,phase:t<ae?"anticipate":t<re?"reach":t<re+.7?"settle":"hold",root:{x:rootX,y:o.y},head:{x:rootX+c.head.offset_x,y:o.y+c.head.offset_y},shoulder,elbow:ik.elbow,wrist:ik.wrist,requestedWrist:desired,fingerTip:tip,pelvis:{x:rootX+4,y:o.y+c.pelvis_y},target:{x:b.target_x,y:b.target_y},diagnostics:{reachable:ik.reachable,requestedReachPx:ik.requestedDistance,maxReachPx:c.upper_arm_length+c.forearm_length,upperSegmentErrorPx:ik.upperError,lowerSegmentErrorPx:ik.lowerError,requestedTargetErrorPx:distance(ik.wrist,desired),targetErrorPx:distance(tip,{x:b.target_x,y:b.target_y-1.5})}};
}