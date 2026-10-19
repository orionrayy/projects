const distance=(a,b)=>Math.hypot(b.x-a.x,b.y-a.y);
export function evaluatePoseQuality(scene,state) {
 const endpointErrorPx=distance(state.fingerTip,state.target);
 const maxSegmentErrorPx=Math.max(state.diagnostics.upperSegmentErrorPx,state.diagnostics.lowerSegmentErrorPx);
 const holdContactOk=state.phase!=="hold"||endpointErrorPx<=scene.quality_contract.max_hold_target_error_px;
 const issues=[];
 if(maxSegmentErrorPx>scene.quality_contract.max_ik_segment_error_px)issues.push("IK_SEGMENT_LENGTH");
 if(!holdContactOk)issues.push("HOLD_CONTACT");
 return {endpointErrorPx,maxSegmentErrorPx,holdContactOk,passed:issues.length===0,issues};
}
