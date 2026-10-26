#!/usr/bin/env python3
"""DR2C VORENYX whole-project static audit v2.67.
No APK changes or device actions. Python 3.10+; Pillow/ffprobe are optional.
"""
import argparse, hashlib, json, shutil, subprocess, zipfile
from pathlib import Path

def sha(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def zip_info(p):
    with zipfile.ZipFile(p) as z:
        names=z.namelist()
        bad=z.testzip()
        return {"file":str(p),"bytes":p.stat().st_size,"sha256":sha(p),"entries":len(names),
                "duplicates":len(names)-len(set(names)),"crc":"PASS" if bad is None else "FAIL","first_bad_entry":bad,
                "names":names}

def image_audio_checks(zpath,names):
    out={"png":{"count":0,"failures":[]},"mp3":{"count":0,"failures":[]}}
    try:
        from PIL import Image
        import io
        with zipfile.ZipFile(zpath) as z:
            for n in names:
                if n.lower().endswith(".png"):
                    out["png"]["count"]+=1
                    try:
                        with Image.open(io.BytesIO(z.read(n))) as im: im.verify()
                    except Exception as e: out["png"]["failures"].append({"path":n,"error":str(e)})
    except ImportError: out["png"]["unavailable"]="Pillow not installed"
    ff=shutil.which("ffprobe")
    if ff:
        import tempfile, os
        with zipfile.ZipFile(zpath) as z:
            for n in names:
                if n.lower().endswith(".mp3"):
                    out["mp3"]["count"]+=1; tmp=None
                    try:
                        fd,tmp=tempfile.mkstemp(suffix=".mp3"); os.close(fd); Path(tmp).write_bytes(z.read(n))
                        r=subprocess.run([ff,"-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",tmp],capture_output=True,text=True,timeout=20)
                        if r.returncode: out["mp3"]["failures"].append({"path":n,"error":r.stderr.strip()})
                    except Exception as e: out["mp3"]["failures"].append({"path":n,"error":str(e)})
                    finally:
                        if tmp:
                            try: Path(tmp).unlink()
                            except OSError: pass
    else: out["mp3"]["unavailable"]="ffprobe not installed"
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-apk",required=True,type=Path); ap.add_argument("--candidate-apk",required=True,type=Path); ap.add_argument("--out",required=True,type=Path)
    args=ap.parse_args(); base=zip_info(args.base_apk); cand=zip_info(args.candidate_apk)
    bset,cset=set(base["names"]),set(cand["names"])
    with zipfile.ZipFile(args.base_apk) as b, zipfile.ZipFile(args.candidate_apk) as c:
        common=sorted(bset&cset); changed=[n for n in common if b.read(n)!=c.read(n)]
        scripts=sorted(n for n in cset if n.startswith("assets/deathforth/") and n.endswith(".df"))
        script_counts={}
        for token in ("cyoa:","cyoa-choice:","cyoa-blank:","cyoa-bridge:"):
            script_counts[token]={"base":0,"candidate":0}
            for n in bset:
                if n.startswith("assets/deathforth/") and n.endswith(".df"): script_counts[token]["base"]+=b.read(n).count(token.encode())
            for n in scripts: script_counts[token]["candidate"]+=c.read(n).count(token.encode())
        assets=image_audio_checks(args.candidate_apk,cand["names"])
        libdiff=[]
        for n in sorted(x for x in common if x.startswith("lib/") and x.endswith("libmain.so")):
            x,y=b.read(n),c.read(n); ranges=[]; i=0
            while i<min(len(x),len(y)):
                if x[i]!=y[i]:
                    j=i+1
                    while j<min(len(x),len(y)) and x[j]!=y[j]: j+=1
                    ranges.append([i,j-1]); i=j
                else: i+=1
            if len(x)!=len(y): ranges.append([min(len(x),len(y)),max(len(x),len(y))-1])
            libdiff.append({"path":n,"base_bytes":len(x),"candidate_bytes":len(y),"changed_bytes":sum(r[1]-r[0]+1 for r in ranges),"changed_ranges":len(ranges)})
        result={"project":"DR2C VORENYX","checkpoint":"v2.67 whole-project static audit","runtime_verified":False,
            "base":{k:v for k,v in base.items() if k!="names"},"candidate":{k:v for k,v in cand.items() if k!="names"},
            "archive_diff":{"common_paths":len(common),"byte_identical_common":len(common)-len(changed),"changed_common":len(changed),"base_only":sorted(bset-cset),"candidate_only":sorted(cset-bset)},
            "deathforth":{"script_count":len(scripts),"changed_vs_base":[n for n in scripts if n in bset and b.read(n)!=c.read(n)],"cyoa_token_counts":script_counts},
            "native_libs":libdiff,"assets":assets,
            "known_static_findings":[
                {"id":"ASSET-001","status":"CONFIRMED","finding":"Splash artwork displays stale V2.43 badge."},
                {"id":"ASSET-002","status":"NOT_PROVEN","finding":"vorenyx_title_screen.png has no literal loader reference in scanned text/code/resource strings; dynamic loading remains possible."},
                {"id":"TEXT-001","status":"CONFIRMED_LABEL_INCONSISTENCY","finding":"fitness is rendered as bugar in native .rodata but mapped as fisik by the boot helper."},
                {"id":"FLOW-001","status":"UNRESOLVED","finding":"Start and install errors require Android PackageManager and Logcat evidence."}],
            "limits":["Heuristic ZIP/source/assets audit, not a complete Deathforth parser or Android runtime test.","Official Android SDK apksigner and device installation were not run.","Do not declare Start fixed from static token counts alone."]}
    args.out.parent.mkdir(parents=True,exist_ok=True); args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"out":str(args.out),"sha256":sha(args.out),"candidate_crc":cand["crc"],"candidate_duplicates":cand["duplicates"],"scripts":len(scripts),"changed_common":len(changed)},indent=2))
if __name__=="__main__": main()
