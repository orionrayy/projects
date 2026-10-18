#!/usr/bin/env node
/** Measure browser SVG rasterization against FFmpeg/librsvg. Diagnostic only; no calibrated gate yet. */
import fs from "node:fs/promises";
import path from "node:path";
import os from "node:os";
import crypto from "node:crypto";
import {spawnSync} from "node:child_process";
import {fileURLToPath,pathToFileURL} from "node:url";
import {renderSceneSvg} from "../src/svg-renderer.mjs";
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),"..");
const [sceneArg="scenes/scene-001.json",outputArg="out/raster-parity-report.json"]=process.argv.slice(2);
const scenePath=path.resolve(ROOT,sceneArg),outputPath=path.resolve(ROOT,outputArg),sampleFrames=[0,24,36,48,72,95];
function command(binary,args,timeout=60000){const r=spawnSync(binary,args,{encoding:"utf8",timeout,maxBuffer:1024*1024});if(r.error)throw r.error;return r;}
function requireOk(r,label,allowDifferenceExit=false){if(r.status===0||(allowDifferenceExit&&r.status===1))return;throw new Error(label+" failed ("+r.status+"): "+(r.stderr||r.stdout));}
function locateBrowser(){const r=command("bash",["-lc","command -v google-chrome || command -v chromium || command -v chromium-browser || true"]);const bin=r.stdout.trim().split("\n").filter(Boolean)[0];if(!bin)throw new Error("No Chromium/Chrome binary found; raster parity cannot be measured.");return bin;}
function parseMetric(value){const text=value.trim(),normalized=text.match(/\(([0-9.]+)\)/),raw=text.match(/^([0-9.]+)/);if(!normalized)throw new Error("Cannot parse ImageMagick MAE metric: "+text);return {raw_mean_absolute_error:raw?Number(raw[1]):null,normalized_mean_absolute_error:Number(normalized[1]),raw_output:text};}
async function main(){
 const scene=JSON.parse(await fs.readFile(scenePath,"utf8")),browser=locateBrowser(),browserVersion=command(browser,["--version"],15000),ffmpegVersion=command("ffmpeg",["-version"]);
 requireOk(browserVersion,"browser version check");requireOk(ffmpegVersion,"FFmpeg version check");
 requireOk(command("bash",["-lc","command -v identify"]),"ImageMagick identify");requireOk(command("bash",["-lc","command -v compare"]),"ImageMagick compare");requireOk(command("bash",["-lc","command -v montage"]),"ImageMagick montage");
 const evidenceDir=path.resolve(ROOT,"out/raster-parity-evidence");
 await fs.rm(evidenceDir,{recursive:true,force:true});await fs.mkdir(evidenceDir,{recursive:true});
 const temp=await fs.mkdtemp(path.join(os.tmpdir(),"motion-studio-raster-parity-")),results=[];
 try{
  for(const frameIndex of sampleFrames){
   const label=String(frameIndex).padStart(3,"0");
   const svg=renderSceneSvg(scene,frameIndex),svgPath=path.join(temp,"frame-"+frameIndex+".svg");
   const rasterPath=path.join(evidenceDir,"ffmpeg-frame-"+label+".png");
   const browserPath=path.join(evidenceDir,"browser-frame-"+label+".png");
   const diffPath=path.join(evidenceDir,"diff-frame-"+label+".png");
   await fs.writeFile(svgPath,svg,"utf8");
   const raster=command("ffmpeg",["-hide_banner","-loglevel","error","-y","-i",svgPath,"-frames:v","1",rasterPath]);requireOk(raster,"FFmpeg SVG rasterization frame "+frameIndex);
   const shot=command(browser,["--headless=new","--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--disable-extensions","--hide-scrollbars","--force-device-scale-factor=1","--window-size="+scene.canvas.width+","+scene.canvas.height,"--screenshot="+browserPath,pathToFileURL(svgPath).href]);requireOk(shot,"Chrome screenshot frame "+frameIndex);
   const browserSize=command("identify",["-format","%wx%h",browserPath]),ffmpegSize=command("identify",["-format","%wx%h",rasterPath]);requireOk(browserSize,"browser PNG dimensions");requireOk(ffmpegSize,"FFmpeg PNG dimensions");
   const expected=scene.canvas.width+"x"+scene.canvas.height;if(browserSize.stdout!==ffmpegSize.stdout||browserSize.stdout!==expected)throw new Error("Raster dimensions differ at frame "+frameIndex+": browser="+browserSize.stdout+", FFmpeg="+ffmpegSize.stdout);
   const diff=command("compare",["-metric","MAE",browserPath,rasterPath,diffPath]);requireOk(diff,"MAE comparison frame "+frameIndex,true);
   results.push({frame_index:frameIndex,dimensions:browserSize.stdout,svg_sha256:crypto.createHash("sha256").update(svg).digest("hex"),
    browser_png:path.relative(ROOT,browserPath),ffmpeg_png:path.relative(ROOT,rasterPath),difference_png:path.relative(ROOT,diffPath),
    ...parseMetric(diff.stderr||diff.stdout)});
  }
  const diffArgs=["-background","#f5f6f8","-fill","#253247","-pointsize","16"];
  for(const result of results){
   diffArgs.push("-label","frame "+result.frame_index+" | MAE "+result.normalized_mean_absolute_error.toFixed(6),path.resolve(ROOT,result.difference_png));
  }
  diffArgs.push("-tile","3x2","-geometry","640x360+8+22",path.join(evidenceDir,"difference-contact-sheet.jpg"));
  requireOk(command("montage",diffArgs),"difference contact sheet");
  const pairArgs=["-background","#f5f6f8","-fill","#253247","-pointsize","14"];
  for(const result of results){
   pairArgs.push("-label","Browser frame "+result.frame_index,path.resolve(ROOT,result.browser_png));
   pairArgs.push("-label","FFmpeg frame "+result.frame_index,path.resolve(ROOT,result.ffmpeg_png));
  }
  pairArgs.push("-tile","3x4","-geometry","426x240+6+18",path.join(evidenceDir,"browser-vs-ffmpeg-contact-sheet.jpg"));
  requireOk(command("montage",pairArgs),"browser versus FFmpeg contact sheet");
 }finally{await fs.rm(temp,{recursive:true,force:true});}
 const vals=results.map(x=>x.normalized_mean_absolute_error),report={
  report_schema_version:"1.0.0",status:"MEASURED_UNCALIBRATED",purpose:"Quantify rasterizer differences; no pass/fail threshold is defined yet.",
  source_scene:path.relative(ROOT,scenePath),evidence_directory:path.relative(ROOT,evidenceDir),
  rasterizers:{browser:browserVersion.stdout.trim(),ffmpeg:ffmpegVersion.stdout.split("\n")[0].trim(),comparison_metric:"ImageMagick mean absolute error (MAE)"},
  sample_frames:sampleFrames,
  summary:{sample_count:results.length,mean_normalized_mae:Number((vals.reduce((a,b)=>a+b,0)/vals.length).toFixed(8)),max_normalized_mae:Number(Math.max(...vals).toFixed(8)),min_normalized_mae:Number(Math.min(...vals).toFixed(8))},
  calibration_policy:"Inspect output differences and font/environment parity before selecting a threshold. MAE is not an aesthetic score.",results
 };
 await fs.mkdir(path.dirname(outputPath),{recursive:true});await fs.writeFile(outputPath,JSON.stringify(report,null,2)+"\n","utf8");console.log(JSON.stringify(report,null,2));
}
main().catch(e=>{console.error(e?.stack||String(e));process.exitCode=1;});