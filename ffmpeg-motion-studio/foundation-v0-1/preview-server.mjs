import http from "node:http";
import fs from "node:fs/promises";
import path from "node:path";
import {fileURLToPath} from "node:url";

const root=path.dirname(fileURLToPath(import.meta.url));
const host=process.env.HOST||"127.0.0.1";
const port=Number(process.env.PORT||4173);
const mime={".html":"text/html; charset=utf-8",".mjs":"text/javascript; charset=utf-8",".js":"text/javascript; charset=utf-8",".json":"application/json; charset=utf-8",".css":"text/css; charset=utf-8",".svg":"image/svg+xml"};

http.createServer(async(req,res)=>{
  try {
    const pathname=decodeURIComponent(new URL(req.url,"http://"+req.headers.host).pathname);
    const relative=pathname==="/"?"preview/index.html":pathname.slice(1);
    const target=path.resolve(root,relative);
    if(target!==root&&!target.startsWith(root+path.sep)){res.writeHead(403);res.end("Forbidden");return;}
    const stat=await fs.stat(target);
    const file=stat.isDirectory()?path.join(target,"index.html"):target;
    const body=await fs.readFile(file);
    res.writeHead(200,{"Content-Type":mime[path.extname(file)]||"application/octet-stream","Cache-Control":"no-store","X-Content-Type-Options":"nosniff"});
    res.end(body);
  } catch {
    res.writeHead(404,{"Content-Type":"text/plain; charset=utf-8"});
    res.end("Not found");
  }
}).listen(port,host,()=>console.log("Motion Studio preview: http://"+host+":"+port+"/preview/"));
