const distance=(a,b)=>Math.hypot(b.x-a.x,b.y-a.y);
const deg=r=>r*180/Math.PI;
const angularDistance=(a,b)=>Math.abs(Math.atan2(Math.sin(a-b),Math.cos(a-b)));
export function evaluatePoseQuality(scene,state) {
 const expected=Math.atan2(state.target.y-state.wrist.y,state.target.x-state.wrist.x);
 const handAimErrorDegrees=deg(angularDistance(state.handAngle,expected));
 const endpointErrorPx=distance(state.fingerTip,state.target);
 const maxSegmentErrorPx=Math.max(state.diagnostics.upperSegmentErrorPx,state.diagnostics.lowerSegmentErrorPx);
 const holdContactOk=state.phase!=="hold"||endpointErrorPx<=scene.quality_contract.max_hold_target_error_px;
 const issues=[];
 if(maxSegmentErrorPx>scene.quality_contract.max_ik_segment_error_px)issues.push("IK_SEGMENT_LENGTH");
 if(handAimErrorDegrees>scene.quality_contract.max_hand_aim_error_degrees)issues.push("HAND_AIM");
 if(!holdContactOk)issues.push("HOLD_CONTACT");
 return {handAimErrorDegrees,endpointErrorPx,maxSegmentErrorPx,holdContactOk,passed:issues.length===0,issues};
}
