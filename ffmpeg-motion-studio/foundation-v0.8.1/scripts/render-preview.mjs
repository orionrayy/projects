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
function legSvg(leg,foot,scene,near) {
  let s=seg(leg.hip,leg.knee,19,near?scene.character.pants:"#58677B","#263347");
  s+=seg(leg.knee,leg.ankle,15,near?scene.character.pants:"#58677B","#263347");
  s+=dot(leg.knee,6,near?"#40516A":"#657286","#263347");
  s+='<g transform="translate('+n(foot.x)+' '+n(foot.y-2)+') rotate('+n(deg(foot.angle||0))+')">'+
    '<path d="M -13 -5 Q -11 -10 -4 -8 L 5 -6 L 13 -2 Q 19 0 17 3 Q 16 5 10 5 L -9 5 Q -16 4 -13 -5 Z" fill="#202A3A"/>'+
    '<path d="M -10 -5 Q -8 -8 -3 -6 L 6 -4 L 12 0 L -11 0 Z" fill="'+scene.character.shoe+'"/>'+
    '<path d="M -12 3 L 15 3" stroke="#E9E7DE" stroke-width="1.7" stroke-linecap="round"/></g>';
  return s;
}
function armSvg(arm,scene,sleeve,near) {
  let s=seg(arm.shoulder,arm.elbow,13,sleeve,"#203348");
  s+=seg(arm.elbow,arm.wrist,9,scene.character.skin,"#7B5544");
  s+=dot(arm.elbow,4.5,scene.character.skin,"#7B5544");
  s+='<circle cx="'+n(arm.wrist.x)+'" cy="'+n(arm.wrist.y)+'" r="5.4" fill="'+scene.character.skin+'" stroke="#7B5544" stroke-width="1.3"/>';
  const sign=near?1:-1;
  for(let i=0;i<3;i++) s+='<path d="M '+n(arm.wrist.x+sign)+' '+n(arm.wrist.y+i*1.7)+' l '+(sign*4)+' 1" stroke="#9A6A50" stroke-width="1.2" stroke-linecap="round"/>';
  return s;
}
function headSvg(p,scene) {
  const h=p.head,neck=p.neck,r=scene.character.head_radius_px,c=scene.character;
  let s='<g transform="rotate('+n(deg(p.headAngle))+' '+n(neck.x)+' '+n(neck.y)+')">';
  s+='<circle cx="'+n(h.x)+'" cy="'+n(h.y)+'" r="'+(r+1.8)+'" fill="#6D4A3D"/>';
  s+='<circle cx="'+n(h.x)+'" cy="'+n(h.y)+'" r="'+r+'" fill="'+c.skin+'"/>';
  s+='<path d="M '+n(h.x-r+1)+' '+n(h.y-5)+' C '+n(h.x-r-2)+' '+n(h.y-r*.9)+', '+n(h.x+r*.38)+' '+n(h.y-r*1.22)+', '+n(h.x+r)+' '+n(h.y-5)+' L '+n(h.x+r-2)+' '+n(h.y-16)+' Q '+n(h.x+8)+' '+n(h.y-24)+' '+n(h.x-5)+' '+n(h.y-19)+' Q '+n(h.x-14)+' '+n(h.y-12)+' '+n(h.x-r+1)+' '+n(h.y-5)+' Z" fill="'+c.hair+'"/>';
  s+='<path d="M '+n(h.x-15)+' '+n(h.y-7)+' q 5 -3 9 0 M '+n(h.x+5)+' '+n(h.y-7)+' q 5 -3 9 0" fill="none" stroke="#6D4A3D" stroke-width="1.8" stroke-linecap="round"/>';
  s+='<ellipse cx="'+n(h.x-10.5)+'" cy="'+n(h.y-1.5)+'" rx="2.6" ry="3.3" fill="#252A31"/><ellipse cx="'+n(h.x+9.5)+'" cy="'+n(h.y-1.5)+'" rx="2.6" ry="3.3" fill="#252A31"/>';
  s+='<path d="M '+n(h.x)+' '+n(h.y+2)+' l -1.5 6 l 4 1 M '+n(h.x-7)+' '+n(h.y+13)+' Q '+n(h.x)+' '+n(h.y+16)+' '+n(h.x+8)+' '+n(h.y+12)+'" fill="none" stroke="#8D5144" stroke-width="1.7" stroke-linecap="round"/>';
  return s+'</g>';
}
function basketSvg(p,scene) {
  const b=p.basket,prop=scene.prop,cx=b.x+b.width/2;
  let s='<path d="M '+n(b.handleLeft.x)+' '+n(b.y+4)+' Q '+n(cx)+' '+n(b.y-17)+' '+n(b.handleRight.x)+' '+n(b.y+4)+'" fill="none" stroke="'+prop.handle_color+'" stroke-width="5" stroke-linecap="round"/>';
  s+='<path d="M '+n(b.x+2)+' '+n(b.y+8)+' Q '+n(cx)+' '+n(b.y+12)+' '+n(b.x+b.width-2)+' '+n(b.y+8)+' L '+n(b.x+b.width-8)+' '+n(b.y+b.height)+' Q '+n(cx)+' '+n(b.y+b.height+3)+' '+n(b.x+7)+' '+n(b.y+b.height)+' Z" fill="'+prop.basket_color+'" stroke="#8A542C" stroke-width="2.2"/>';
  s+='<path d="M '+n(b.x+7)+' '+n(b.y+19)+' L '+n(b.x+b.width-7)+' '+n(b.y+19)+' M '+n(b.x+9)+' '+n(b.y+29)+' L '+n(b.x+b.width-9)+' '+n(b.y+29)+'" stroke="#C87528" stroke-width="2"/>';
  s+='<rect x="'+n(b.x+2)+'" y="'+n(b.y+6)+'" width="'+n(b.width-4)+'" height="7" rx="3.5" fill="#B96D2A" stroke="#8A542C" stroke-width="1.2"/>';
  return s;
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
  s+=armSvg(p.farArm,scene,"#2F6D8D",false);
  const pel=p.pelvis,chest=p.chest,near=p.shoulders.near,far=p.shoulders.far;
  s+='<path d="M '+n(far.x-8)+' '+n(far.y-1)+' Q '+n(chest.x)+' '+n(chest.y-13)+' '+n(near.x+12)+' '+n(near.y-2)+' L '+n(pel.x+18)+' '+n(pel.y+2)+' Q '+n(pel.x)+' '+n(pel.y+13)+' '+n(pel.x-17)+' '+n(pel.y+2)+' Z" fill="'+c.shirt+'" stroke="#203348" stroke-width="2.7" stroke-linejoin="round"/>';
  s+='<path d="M '+n(chest.x-12)+' '+n(chest.y+11)+' Q '+n(chest.x)+' '+n(chest.y+17)+' '+n(chest.x+13)+' '+n(chest.y+10)+'" fill="none" stroke="'+c.shirt_shadow+'" stroke-width="2.5"/>';
  s+=seg(p.neck,{x:p.chest.x,y:p.chest.y+4},11,c.skin,"#7B5544");
  s+=headSvg(p,scene)+basketSvg(p,scene)+armSvg(p.nearArm,scene,"#3A82A3",true);
  s+='<rect x="34" y="28" width="388" height="82" rx="14" fill="#FFFEFA" opacity=".92" stroke="#DAD5C7"/>';
  s+='<text x="54" y="57" font-family="DejaVu Sans,sans-serif" font-size="18" font-weight="700" fill="#243345">MOTION STUDIO / v0.8.1</text>';
  s+='<text x="54" y="82" font-family="DejaVu Sans,sans-serif" font-size="14" fill="#526173">'+(mode==="carry"?"Carry interaction + hand contact":"Free-arm counter-swing")+'</text>';
  s+='<text x="54" y="99" font-family="DejaVu Sans,sans-serif" font-size="11" fill="#697687">FRAME '+String(frameIndex+1).padStart(3,"0")+' / '+scene.duration_frames+' TIME '+n(p.timeSeconds)+' s</text>';
  s+='<text x="34" y="690" font-family="DejaVu Sans,sans-serif" font-size="12" fill="#716B60">Geometry diagnostics are not an artistic-naturalness score.</text>';
  s+='<text x="'+(scene.canvas.width-34)+'" y="690" text-anchor="end" font-family="DejaVu Sans,sans-serif" font-size="12" fill="#716B60">24 FPS · Procedural 2D preview</text></svg>';
  return s;
}
export function summarizeScene(scene,armMode) {
  const mode=armMode||scene.motion.arm_mode||"carry",poses=[];
  for(let i=0;i<scene.duration_frames;i++) poses.push(evaluateLocomotion(scene,i,mode));
  const vals=(fn)=>poses.map(fn),sep=vals(p=>p.leftFoot.x-p.rightFoot.x);
  const torso=vals(p=>deg(p.torsoAngle)),head=vals(p=>deg(p.headAngle));
  const finite=poses.every(p=>[p.rootX,p.pelvis.x,p.pelvis.y,p.chest.x,p.chest.y,p.head.x,p.head.y,p.nearArm.elbow.x,p.nearArm.elbow.y,p.farArm.elbow.x,p.farArm.elbow.y,p.leftFoot.x,p.leftFoot.y,p.rightFoot.x,p.rightFoot.y,p.diagnostics.boneLengthErrorPx,p.diagnostics.basketContactErrorPx,p.diagnostics.groundPenetrationPx].every(Number.isFinite));
  if(!finite) throw new Error("Non-finite pose value detected during preview preflight.");
  return {schemaVersion:"1.0.0",sceneId:scene.scene_id,sceneVersion:scene.scene_version,armMode:mode,frameCount:scene.duration_frames,fps:scene.fps,durationSeconds:scene.duration_frames/scene.fps,canvas:scene.canvas,deterministicPoseSampling:true,allPoseValuesFinite:finite,minProjectedFootSeparationPx:Math.min(...sep),maxBoneLengthErrorPx:Math.max(...vals(p=>p.diagnostics.boneLengthErrorPx)),maxBasketContactErrorPx:Math.max(...vals(p=>p.diagnostics.basketContactErrorPx)),maxGroundPenetrationPx:Math.max(...vals(p=>p.diagnostics.groundPenetrationPx)),maxAnkleClampErrorPx:Math.max(...vals(p=>p.diagnostics.ankleClampErrorPx)),torsoAngleRangeDegrees:Math.max(...torso)-Math.min(...torso),headAngleRangeDegrees:Math.max(...head)-Math.min(...head),minNearArmElbowAngleDegrees:Math.min(...vals(p=>p.nearArm.elbowAngleDegrees)),maxNearArmElbowAngleDegrees:Math.max(...vals(p=>p.nearArm.elbowAngleDegrees)),humanVisualAcceptance:"pending",pixelLevelNaturalnessMeasurement:"not_performed",browserFfmpegRasterParity:"not_verified",note:"Passing geometry metrics do not establish natural motion, artistic quality, or production readiness."};
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
  const manifest={schemaVersion:"1.0.0",generator:"Motion Studio v0.8.1 SVG preview",producedAt:"deterministic-build",scenes:results.map(x=>x.summary),productionStatus:"prototype",visualReviewRequired:true};
  fs.writeFileSync(path.join(out,"render-manifest.json"),JSON.stringify(manifest,null,2)+"\n","utf8");
  process.stdout.write(JSON.stringify({outputDir:out,scenes:manifest.scenes.map(x=>({mode:x.armMode,frames:x.frameCount,durationSeconds:x.durationSeconds,finite:x.allPoseValuesFinite}))},null,2)+"\n");
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)) run();
