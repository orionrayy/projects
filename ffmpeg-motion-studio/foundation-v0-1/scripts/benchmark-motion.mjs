#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";
import {evaluateFrame,distance} from "../src/motion-core.mjs";
import {inspectSceneLayout} from "../src/layout-guards.mjs";
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const [sceneArg="scenes/scene-001.json",suiteArg="benchmarks/motion-scenarios.json",outputArg="out/motion-benchmark-report.json"]=process.argv.slice(2);
const [scenePath,suitePath,outputPath]=[sceneArg,suiteArg,outputArg].map(p=>path.resolve(ROOT,p));
const round=n=>Number(n.toFixed(4));
async function main(){
 const [base,suite]=await Promise.all([fs.readFile(scenePath,"utf8").then(JSON.parse),fs.readFile(suitePath,"utf8").then(JSON.parse)]);
 const results=[];
 for(const scenario of suite.cases){
  const scene=structuredClone(base);scene.board.target_x=scenario.target_x;scene.board.target_y=scenario.target_y;
  scene.character.upper_arm_length=scenario.upper_arm_length;scene.character.forearm_length=scenario.forearm_length;
  const states=Array.from({length:scene.duration_frames},(_,frame)=>evaluateFrame(scene,frame));
  const segmentErrors=states.flatMap(s=>[s.diagnostics.upperSegmentErrorPx,s.diagnostics.lowerSegmentErrorPx]);
  const positions=states.map(s=>s.wrist),steps=positions.slice(1).map((p,i)=>distance(positions[i],p));
  const accelerations=steps.slice(1).map((v,i)=>Math.abs(v-steps[i]));
  const endpoint=states.at(-1),endpointReachable=endpoint.diagnostics.reachable,endpointTargetError=distance(endpoint.fingerTip,endpoint.target);
  const layoutIssues=inspectSceneLayout(scene).map(x=>x.code),maxSegmentError=Math.max(...segmentErrors),maxStep=Math.max(...steps),maxAcceleration=Math.max(0,...accelerations);
  const unreachableFrames=states.filter(s=>!s.diagnostics.reachable).length;
  const passed=maxSegmentError<=suite.thresholds.max_segment_error_px&&maxStep<=suite.thresholds.max_step_px_per_frame
   &&maxAcceleration<=suite.thresholds.max_acceleration_px_per_frame_squared&&endpointReachable===scenario.expected_endpoint_reachable
   &&(!scenario.expected_endpoint_reachable||unreachableFrames===0)
   &&(!scenario.expected_endpoint_reachable||endpointTargetError<=suite.thresholds.reachable_target_error_px);
  results.push({id:scenario.id,status:passed?"PASS":"FAIL",frames_evaluated:states.length,expected_endpoint_reachable:scenario.expected_endpoint_reachable,
   observed_endpoint_reachable:endpointReachable,unreachable_frames:unreachableFrames,settle_amplitude_requested_px:scene.motion.settle_amplitude_px,
   settle_amplitude_used_last_settle_frame_px:round(endpoint.diagnostics.settleAmplitudeUsedPx),max_segment_length_error_px:round(maxSegmentError),
   max_wrist_step_px_per_frame:round(maxStep),max_wrist_acceleration_px_per_frame_squared:round(maxAcceleration),
   endpoint_target_error_px:round(endpointTargetError),layout_issues:layoutIssues});
 }
 const failed=results.filter(x=>x.status!=="PASS"),report={report_schema_version:"1.0.0",benchmark_id:"motion-studio-foundation-synthetic-motion-v0.2",
  evidence_class:"SYNTHETIC_ENGINEERING_BENCHMARK",source_scene:path.relative(ROOT,scenePath),scenario_suite:path.relative(ROOT,suitePath),
  frames_per_case:base.duration_frames,threshold_note:"Thresholds are engineering regression limits for this pilot, not universal human-motion or aesthetic standards.",
  summary:{cases:results.length,passed:results.length-failed.length,failed:failed.length,status:failed.length?"FAIL":"PASS"},results};
 await fs.mkdir(path.dirname(outputPath),{recursive:true});await fs.writeFile(outputPath,JSON.stringify(report,null,2)+"\n","utf8");
 console.log(JSON.stringify(report,null,2));if(failed.length)process.exitCode=1;
}
main().catch(error=>{console.error(error?.stack||String(error));process.exitCode=1;});