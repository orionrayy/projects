import { evaluateFrame } from "../src/motion-core.mjs";
import { renderSceneSvg } from "../src/svg-renderer.mjs";
import { inspectSceneLayout } from "../src/layout-guards.mjs";
const $=id=>document.getElementById(id),viewport=$("viewport"),slider=$("frame"),playButton=$("play");
let originalScene,scene,isPlaying=false,diagnostics=false,handle=null,lastTick=0,accumulator=0,currentFrame=0,referenceA=null,compareVisible=false;
const clone=value=>structuredClone(value);
function formatTime(seconds){const minutes=Math.floor(seconds/60),rest=seconds-minutes*60;return String(minutes).padStart(2,"0")+":"+rest.toFixed(3).padStart(6,"0");}
function syncLabels(){
 $("target-x-value").textContent=String(scene.board.target_x);$("target-y-value").textContent=String(scene.board.target_y);
 $("upper-value").textContent=scene.character.upper_arm_length+" px";$("forearm-value").textContent=scene.character.forearm_length+" px";
 $("anticipation-value").textContent=scene.motion.anticipation_px+" px";$("settle-value").textContent=scene.motion.settle_amplitude_px+" px";
 for(const [id,value] of [["target-x",scene.board.target_x],["target-y",scene.board.target_y],["upper",scene.character.upper_arm_length],["forearm",scene.character.forearm_length],["anticipation",scene.motion.anticipation_px],["settle",scene.motion.settle_amplitude_px]])$(id).value=String(value);
 $("elbow-bend").textContent="Elbow bend: "+(scene.motion.elbow_bend>0?"positive":"negative");
 $("dirty-state").textContent=JSON.stringify(scene)===JSON.stringify(originalScene)?"BASELINE":"MODIFIED";
}
function updateStatus(state){
 const issues=inspectSceneLayout(scene),messages=[];
 if(!state.diagnostics.reachable)messages.push("IK UNREACHABLE");
 if(issues.length)messages.push("LAYOUT "+issues.map(x=>x.code).join(", "));
 const warning=messages.length>0;$("status").textContent=warning?messages.join(" · "):"Scene loaded · "+state.phase;
 $("status").classList.toggle("warn",warning);$("status-dot").style.background=warning?"#d97706":"#1f9d73";
 $("reachability").textContent=state.diagnostics.reachable?"YES":"NO — TARGET CLAMPED";$("reachability").classList.toggle("warn",!state.diagnostics.reachable);
 $("error").textContent=Math.max(state.diagnostics.upperSegmentErrorPx,state.diagnostics.lowerSegmentErrorPx).toFixed(4)+" px";
 $("layout-status").textContent=issues.length?issues.length+" ISSUE(S)":"PASS";$("layout-status").classList.toggle("warn",issues.length>0);
}
function renderFrame(frame){
 currentFrame=Math.max(0,Math.min(scene.duration_frames-1,Math.trunc(frame)));const state=evaluateFrame(scene,currentFrame);
 viewport.innerHTML=renderSceneSvg(scene,currentFrame,{showDiagnostics:diagnostics});slider.value=String(currentFrame);
 $("frame-label").textContent=currentFrame+" / "+(scene.duration_frames-1);
 $("timecode").textContent=formatTime(currentFrame/scene.fps)+" / "+formatTime(scene.duration_frames/scene.fps);
 updateStatus(state);syncLabels();
 if(compareVisible&&referenceA){$("viewport-a").innerHTML=renderSceneSvg(referenceA,currentFrame,{showDiagnostics:diagnostics});$("viewport-b").innerHTML=renderSceneSvg(scene,currentFrame,{showDiagnostics:diagnostics});}
}
function stop(){isPlaying=false;playButton.textContent="Play";if(handle!==null)cancelAnimationFrame(handle);handle=null;lastTick=0;accumulator=0;}
function tick(now){if(!isPlaying)return;if(!lastTick)lastTick=now;accumulator+=now-lastTick;lastTick=now;const frameMs=1000/scene.fps,steps=Math.floor(accumulator/frameMs);if(steps>0){accumulator-=steps*frameMs;renderFrame((currentFrame+steps)%scene.duration_frames);}handle=requestAnimationFrame(tick);}
function mutate(fn){stop();fn(scene);renderFrame(currentFrame);}
playButton.addEventListener("click",()=>{if(!scene)return;if(isPlaying){stop();return;}isPlaying=true;playButton.textContent="Pause";lastTick=0;handle=requestAnimationFrame(tick);});
slider.addEventListener("input",e=>{stop();renderFrame(Number(e.target.value));});
$("prev").addEventListener("click",()=>{stop();renderFrame(currentFrame-1);});$("next").addEventListener("click",()=>{stop();renderFrame(currentFrame+1);});
$("start").addEventListener("click",()=>{stop();renderFrame(0);});$("reach").addEventListener("click",()=>{stop();renderFrame(Math.round((scene.motion.anticipation_seconds+scene.motion.reach_seconds)*scene.fps));});
$("hold").addEventListener("click",()=>{stop();renderFrame(scene.duration_frames-1);});
$("diagnostics").addEventListener("click",e=>{diagnostics=!diagnostics;e.currentTarget.setAttribute("aria-pressed",String(diagnostics));e.currentTarget.textContent=diagnostics?"Hide rig diagnostics":"Show rig diagnostics";if(scene)renderFrame(currentFrame);});
for(const id of ["target-x","target-y","upper","forearm","anticipation","settle"]){
 $(id).addEventListener("input",e=>mutate(next=>{const v=Number(e.target.value);if(id==="target-x")next.board.target_x=v;else if(id==="target-y")next.board.target_y=v;else if(id==="upper")next.character.upper_arm_length=v;else if(id==="forearm")next.character.forearm_length=v;else if(id==="anticipation")next.motion.anticipation_px=v;else if(id==="settle")next.motion.settle_amplitude_px=v;}));
}
$("elbow-bend").addEventListener("click",()=>mutate(next=>{next.motion.elbow_bend*=-1;}));
$("reset").addEventListener("click",()=>{stop();scene=clone(originalScene);renderFrame(currentFrame);});
$("save-a").addEventListener("click",()=>{referenceA=clone(scene);$("toggle-ab").disabled=false;$("toggle-ab").textContent=compareVisible?"Hide A/B compare":"Show A/B compare";$("dirty-state").textContent="REFERENCE A STORED";if(compareVisible)renderFrame(currentFrame);});
$("toggle-ab").addEventListener("click",()=>{if(!referenceA)return;compareVisible=!compareVisible;$("compare-section").hidden=!compareVisible;$("toggle-ab").textContent=compareVisible?"Hide A/B compare":"Show A/B compare";if(compareVisible)renderFrame(currentFrame);});
try{const response=await fetch("../scenes/scene-001.json",{cache:"no-store"});if(!response.ok)throw new Error("Scene fetch failed: "+response.status+" "+response.statusText);originalScene=await response.json();scene=clone(originalScene);slider.max=String(scene.duration_frames-1);$("fps").textContent=String(scene.fps);syncLabels();renderFrame(0);}
catch(error){$("status").textContent="Load failed";const box=$("error-box");box.hidden=false;box.className="fatal";box.textContent="Preview could not load. Serve project root over HTTP (npm run preview).\n"+(error?.stack||error);}