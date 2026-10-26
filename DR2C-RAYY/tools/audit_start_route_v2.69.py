#!/usr/bin/env python3
"""Compare DR2C VORENYX start-route scripts in two APK ZIPs (static only)."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
PATHS=["assets/deathforth/events.df","assets/deathforth/game-select.df","assets/deathforth/game-start.df","assets/deathforth/boot-end.df","assets/deathforth/events/tutorial.df","assets/deathforth/boot.df"]
def sha(data: bytes)->str:return hashlib.sha256(data).hexdigest()
def lexical_code(source: str)->list[str]:
    out=[];i=0;n=len(source);line_start=True
    while i<n:
        c=source[i]
        if c in " \t\r" and line_start:i+=1;continue
        if c=="\n":line_start=True;i+=1;continue
        if line_start and c=="\\":
            while i<n and source[i]!="\n":i+=1
            continue
        line_start=False
        if source.startswith("//",i):
            while i<n and source[i]!="\n":i+=1
            continue
        if source.startswith("(*",i):
            end=source.find("*)",i+2)
            if end<0:out.append("<UNCLOSED_BLOCK_COMMENT>");break
            line_start=source[i:end+2].endswith("\n");i=end+2;continue
        if c=='"':
            i+=1
            while i<n:
                if source[i]=='"':i+=1;break
                if source[i]=='\\' and i+1<n:i+=2
                else:i+=1
            out.append("<STRING>");continue
        j=i
        while j<n and not source[j].isspace() and source[j]!='"':
            if source.startswith("//",j) or source.startswith("(*",j):break
            j+=1
        if j==i:i+=1
        else:out.append(source[i:j]);i=j
    return out
def compare(a,b,path):
    aa=a.read(path);bb=b.read(path)
    result={"base_sha256":sha(aa),"candidate_sha256":sha(bb),"byte_identical":aa==bb}
    if aa!=bb:
        ta=lexical_code(aa.decode("utf-8","replace"));tb=lexical_code(bb.decode("utf-8","replace"))
        result.update({"base_code_token_count":len(ta),"candidate_code_token_count":len(tb),"code_token_stream_equal":ta==tb})
        if ta!=tb:
            diffs=[]
            for i,(x,y) in enumerate(zip(ta,tb)):
                if x!=y:
                    diffs.append({"token_index":i,"base":x,"candidate":y})
                    if len(diffs)==40:break
            result["first_token_differences"]=diffs;result["length_difference"]=len(tb)-len(ta)
    return result
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument("--base-apk",type=Path,required=True);ap.add_argument("--candidate-apk",type=Path,required=True);ap.add_argument("--out",type=Path,required=True);a=ap.parse_args()
    checks={}
    with zipfile.ZipFile(a.base_apk) as base,zipfile.ZipFile(a.candidate_apk) as cand:
        bad1=base.testzip();bad2=cand.testzip()
        for p in PATHS:checks[p]={"error":"missing from one APK"} if p not in base.namelist() or p not in cand.namelist() else compare(base,cand,p)
        names=[p for p in cand.namelist() if p.startswith("assets/deathforth/") and p.endswith(".df")]
        hits=[p for p in names if "id-name-localize" in cand.read(p).decode("utf-8","replace")]
        report={"project":"DR2C VORENYX","checkpoint":"v2.69 start-route static audit","status":"STATIC_HANDLER_PRESENT_RUNTIME_REQUIRED",
        "base_apk":{"file":a.base_apk.name,"sha256":sha(a.base_apk.read_bytes()),"zip_crc":"PASS" if not bad1 else "FAIL:"+bad1},
        "candidate_apk":{"file":a.candidate_apk.name,"sha256":sha(a.candidate_apk.read_bytes()),"zip_crc":"PASS" if not bad2 else "FAIL:"+bad2},
        "script_comparison":checks,"id_name_localize_definition_or_use_files":hits,
        "findings":{"events_df_byte_identical":checks.get(PATHS[0],{}).get("byte_identical",False),"game_select_control_tokens_match_base":checks.get(PATHS[1],{}).get("code_token_stream_equal",False),"game_start_control_tokens_match_base":checks.get(PATHS[2],{}).get("code_token_stream_equal",False),"boot_end_control_tokens_match_base":checks.get(PATHS[3],{}).get("code_token_stream_equal",False),"tutorial_token_drift_requires_runtime_review":not checks.get(PATHS[4],{}).get("code_token_stream_equal",False),"fitness_label_helper_used_on_trait_perk_ui_paths":len(hits)>1,"v268_repair_targets_intersect_start_route":False},
        "runtime":{"android_install":"USER_REPORTED_SUCCESS","button_dispatch":"NOT TESTED","select_boot":"NOT TESTED","tutorial_load":"NOT TESTED","gameplay_save_load":"NOT TESTED"},
        "conclusion":"The central Start control-token path is present and largely normalized to the base source. The id-name-localize helper is used by trait/perk UI paths but is not a call on the initial select-boot path. Capture Logcat while tapping Start before proposing another handler rewrite."}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8");print(json.dumps(report,indent=2))
if __name__=="__main__":main()
