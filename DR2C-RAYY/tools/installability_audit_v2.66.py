#!/usr/bin/env python3
"""Compact offline DR2C APK installability audit. Does not install or modify APKs.
Requires Python 3.10+, cryptography, and jarsigner for the optional v1 check.
"""
import argparse, hashlib, json, shutil, struct, subprocess, zipfile
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

V2_ID=0x7109871A
MAGIC=b"APK Sig Block 42"
CHUNK=1024*1024

def h(b): return hashlib.sha256(b).hexdigest()
def lp(b,o=0):
    if o+4>len(b): raise ValueError("truncated length prefix")
    n=struct.unpack_from("<I",b,o)[0]
    if o+4+n>len(b): raise ValueError("length prefix overrun")
    return b[o+4:o+4+n],o+4+n
def lp_list(b):
    out=[];o=0
    while o<len(b):
        x,o=lp(b,o);out.append(x)
    return out
def zip_audit(p):
    with zipfile.ZipFile(p) as z:
        n=z.namelist();bad=z.testzip()
        return {"filename":p.name,"bytes":p.stat().st_size,"sha256":h(p.read_bytes()),"entries":len(n),
                "duplicates":len(n)-len(set(n)),"crc":"PASS" if bad is None else "FAIL","first_bad_entry":bad}
def entry(p,z,name):
    i=z.getinfo(name)
    with open(p,"rb") as f:
        f.seek(i.header_offset);head=f.read(30)
    if head[:4]!=b"PK\x03\x04": raise ValueError("invalid local header: "+name)
    fn,ex=struct.unpack_from("<HH",head,26);off=i.header_offset+30+fn+ex
    return {"method":i.compress_type,"size":i.file_size,"offset":off,"mod4":off%4,"mod4096":off%4096}
def verify_v2(p):
    b=p.read_bytes();e=b.rfind(b"PK\x05\x06",max(0,len(b)-65557))
    if e<0:raise ValueError("EOCD absent")
    _,_,_,_,_,cdsize,cdoff,comment=struct.unpack_from("<IHHHHIIH",b,e)
    if e+22+comment!=len(b):raise ValueError("EOCD/comment mismatch")
    if b[cdoff-16:cdoff]!=MAGIC:raise ValueError("APK signing magic absent")
    size=struct.unpack_from("<Q",b,cdoff-24)[0];start=cdoff-(size+8)
    if struct.unpack_from("<Q",b,start)[0]!=size or start+size+8!=cdoff:raise ValueError("signing block length mismatch")
    pairs=[];o=start+8;end=cdoff-24
    while o<end:
        n=struct.unpack_from("<Q",b,o)[0];o+=8
        if n<4 or o+n>end:raise ValueError("signing pair length invalid")
        ident=struct.unpack_from("<I",b,o)[0];pairs.append((ident,b[o+4:o+n]));o+=n
    vals=[v for i,v in pairs if i==V2_ID]
    if len(vals)!=1:raise ValueError("exactly one v2 pair expected")
    signers_blob,endoff=lp(vals[0])
    if endoff!=len(vals[0]):raise ValueError("v2 trailing bytes")
    signers=lp_list(signers_blob)
    if len(signers)!=1:raise ValueError("exactly one signer expected")
    signer=signers[0];o=0;signed,o=lp(signer,o);sigs,o=lp(signer,o);pub,o=lp(signer,o)
    if o!=len(signer):raise ValueError("signer trailing bytes")
    o=0;digests,o=lp(signed,o);certs,o=lp(signed,o);attrs,o=lp(signed,o)
    if o!=len(signed):raise ValueError("signed-data trailing bytes")
    cert=x509.load_der_x509_certificate(lp_list(certs)[0])
    certpub=cert.public_key().public_bytes(serialization.Encoding.DER,serialization.PublicFormat.SubjectPublicKeyInfo)
    if pub!=certpub:raise ValueError("signer key doesn't match leaf certificate")
    sigok=False;alg_used=None
    for rec in lp_list(sigs):
        alg=struct.unpack_from("<I",rec)[0];sig,_=lp(rec,4)
        try:
            if alg==0x0103 and isinstance(cert.public_key(),rsa.RSAPublicKey):
                cert.public_key().verify(sig,signed,padding.PKCS1v15(),hashes.SHA256())
            elif alg==0x0104 and isinstance(cert.public_key(),rsa.RSAPublicKey):
                cert.public_key().verify(sig,signed,padding.PKCS1v15(),hashes.SHA512())
            elif alg==0x0101 and isinstance(cert.public_key(),rsa.RSAPublicKey):
                cert.public_key().verify(sig,signed,padding.PSS(mgf=padding.MGF1(hashes.SHA256()),salt_length=32),hashes.SHA256())
            elif alg==0x0102 and isinstance(cert.public_key(),rsa.RSAPublicKey):
                cert.public_key().verify(sig,signed,padding.PSS(mgf=padding.MGF1(hashes.SHA512()),salt_length=64),hashes.SHA512())
            else: continue
            sigok=True;alg_used=alg;break
        except Exception: continue
    if not sigok:raise ValueError("no recognized v2 signer signature verified")
    chunks=[]
    def add(region):
        for i in range(0,len(region),CHUNK):
            c=region[i:i+CHUNK];chunks.append(hashlib.sha256(b"\xa5"+struct.pack("<I",len(c))+c).digest())
    add(b[:start]);add(b[cdoff:e])
    eocd=bytearray(b[e:]);struct.pack_into("<I",eocd,16,start);add(bytes(eocd))
    calculated=hashlib.sha256(b"\x5a"+struct.pack("<I",len(chunks))+b"".join(chunks)).digest()
    matched=False;digest_alg=None
    for rec in lp_list(digests):
        alg=struct.unpack_from("<I",rec)[0];dg,_=lp(rec,4)
        if alg in (0x0101,0x0103) and dg==calculated:matched=True;digest_alg=alg;break
    if not matched:raise ValueError("v2 content digest mismatch/unsupported digest alg")
    return {"status":"PASS_INDEPENDENT_CRYPTOGRAPHIC_CHECK","block_start":start,"block_bytes":cdoff-start,
            "pair_ids":[hex(i) for i,_ in pairs],"signer_count":len(signers),"signature_algorithm_id":hex(alg_used),
            "public_key_matches_certificate":True,"signed_data_signature_valid":True,"apk_content_digest_valid":True,
            "content_digest_algorithm_id":hex(digest_alg),"content_digest_chunk_count":len(chunks),
            "certificate_subject":cert.subject.rfc4514_string(),"certificate_sha256":cert.fingerprint(hashes.SHA256()).hex(),
            "official_apksigner":"NOT RUN; use Android SDK Build Tools apksigner for authoritative toolchain verification"}
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--base-apk",type=Path,required=True);a.add_argument("--candidate-apk",type=Path,required=True)
    a.add_argument("--out",type=Path,required=True)
    args=a.parse_args();base=zipfile.ZipFile(args.base_apk);cand=zipfile.ZipFile(args.candidate_apk)
    report={"project":"DR2C VORENYX","checkpoint":"v2.66 compact package audit","status":"STATIC_PASS_RUNTIME_NOT_TESTED",
            "base":zip_audit(args.base_apk),"candidate":zip_audit(args.candidate_apk)}
    common=set(base.namelist())&set(cand.namelist())
    changed=[n for n in sorted(common) if base.read(n)!=cand.read(n)]
    with args.candidate_apk.open("rb") as f:pass
    res=entry(args.candidate_apk,cand,"resources.arsc")
    libs=[{"path":n,**entry(args.candidate_apk,cand,n)} for n in cand.namelist() if n.startswith("lib/") and n.endswith(".so")]
    report["diff"]={"common_entries":len(common),"changed_common_entries":len(changed),"byte_identical_common_entries":len(common)-len(changed),
                    "base_only":sorted(set(base.namelist())-set(cand.namelist())),"candidate_only":sorted(set(cand.namelist())-set(base.namelist()))}
    report["resources_arsc"]={**res,"uncompressed":res["method"]==0,"four_byte_aligned":res["mod4"]==0}
    report["native_libs"]={"count":len(libs),"stored_count":sum(x["method"]==0 for x in libs),
                           "stored_alignment_failures":[x["path"] for x in libs if x["method"]==0 and x["mod4096"]!=0]}
    report["signature_v2"]=verify_v2(args.candidate_apk)
    js=shutil.which("jarsigner")
    if js:
        r=subprocess.run([js,"-verify",str(args.candidate_apk)],capture_output=True,text=True,timeout=180)
        report["signature_v1"]={"status":"PASS" if r.returncode==0 and "jar verified" in (r.stdout+r.stderr).lower() else "FAIL","exit":r.returncode,
                                "tail":"\n".join((r.stdout+r.stderr).splitlines()[-8:])}
    else:report["signature_v1"]={"status":"NOT_RUN_JARSIGNER_MISSING"}
    report["runtime"]={"official_apksigner":"NOT_RUN","android_install":"NOT_TESTED","start_button":"NOT_TESTED","gameplay_save_load":"NOT_TESTED","release_ready":False}
    args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"report":str(args.out),"v2":report["signature_v2"],"v1":report["signature_v1"],"runtime":report["runtime"]},indent=2))
if __name__=="__main__":main()
