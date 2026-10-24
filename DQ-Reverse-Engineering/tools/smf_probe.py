#!/usr/bin/env python3
"""Read-only binary probe for S3D .smf files; it does not unpack/decrypt them."""
import argparse, collections, hashlib, json, math, pathlib, zlib

MAGICS = {
    b"PK\x03\x04": "ZIP", b"\x1f\x8b": "GZIP", b"BZh": "BZIP2",
    b"\xfd7zXZ\x00": "XZ", b"7z\xbc\xaf\x27\x1c": "7-Zip",
    b"Rar!": "RAR", b"\x28\xb5\x2f\xfd": "Zstandard",
    b"\x04\x22\x4d\x18": "LZ4-frame", b"SQLite format 3\x00": "SQLite",
    b"UnityFS": "UnityFS"
}

def entropy(data):
    counts=collections.Counter(data); n=len(data)
    return -sum((v/n)*math.log2(v/n) for v in counts.values()) if n else 0.0

def complete_stream(data, offset, wbits, output_cap=1_048_576):
    dec=zlib.decompressobj(wbits); pos=offset; produced=0
    try:
        while pos<len(data):
            chunk=data[pos:pos+65536]; pos+=len(chunk)
            out=dec.decompress(chunk, output_cap-produced+1); produced+=len(out)
            if produced>output_cap: return "output-limit"
            if dec.eof: return "valid"
            while dec.unconsumed_tail:
                out=dec.decompress(dec.unconsumed_tail, output_cap-produced+1); produced+=len(out)
                if produced>output_cap: return "output-limit"
                if dec.eof: return "valid"
        return "truncated"
    except zlib.error:
        return "invalid"

def scan_compression(data):
    gzip=[]; zlib_headers=[]
    p=0
    while (p:=data.find(b"\x1f\x8b",p))>=0:
        if p+10<=len(data) and data[p+2]==8 and not(data[p+3]&0xe0): gzip.append(p)
        p+=1
    p=0
    while (p:=data.find(b"\x78",p))>=0:
        if p+2<=len(data):
            cmf,flg=data[p],data[p+1]
            if (cmf&15)==8 and (cmf>>4)<=7 and ((cmf<<8)|flg)%31==0: zlib_headers.append(p)
        p+=1
    out={"gzip_candidate_headers":len(gzip),"gzip_validated_complete_streams":0,
         "gzip_output_limit_hits":0,"gzip_invalid_or_truncated":0,
         "zlib_candidate_headers":len(zlib_headers),"zlib_validated_complete_streams":0,
         "zlib_output_limit_hits":0,"zlib_invalid_or_truncated":0,
         "candidate_offset_samples":{"gzip":gzip[:30],"zlib":zlib_headers[:30]},
         "per_candidate_output_limit_bytes":1048576}
    for name, offsets, wbits in (("gzip",gzip,31),("zlib",zlib_headers,15)):
        for offset in offsets:
            result=complete_stream(data,offset,wbits)
            if result=="valid": out[name+"_validated_complete_streams"]+=1
            elif result=="output-limit": out[name+"_output_limit_hits"]+=1
            else: out[name+"_invalid_or_truncated"]+=1
    return out

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("input",type=pathlib.Path); ap.add_argument("--output",type=pathlib.Path)
    ap.add_argument("--max-text-runs",type=int,default=100); a=ap.parse_args()
    data=a.input.read_bytes(); runs=[]; start=None
    for i,b in enumerate(data+b"\x00"):
        if 32<=b<=126 or b in (9,10,13):
            if start is None: start=i
        elif start is not None:
            if i-start>=6: runs.append({"offset":start,"text":data[start:i].decode("ascii","replace")})
            start=None
    hits=[]
    for magic,name in MAGICS.items():
        offset=0
        while len(hits)<2000:
            offset=data.find(magic,offset)
            if offset<0: break
            hits.append({"offset":offset,"format":name,"magic_hex":magic.hex()}); offset+=1
    report={"file":a.input.name,"size_bytes":len(data),
      "sha256":hashlib.sha256(data).hexdigest(),"header_hex":data[:64].hex(" "),
      "entropy_bits_per_byte":round(entropy(data),6),"byte_values_present":len(set(data)),
      "known_magic_candidates":hits,"compression_candidate_validation":scan_compression(data),
      "printable_ascii_runs":runs[:a.max_text_runs],
      "interpretation":"Magic matches are candidates only. High entropy and failed common-format tests do not prove encryption; this probe does not decode the SMF format."}
    rendered=json.dumps(report,indent=2,ensure_ascii=False)
    if a.output: a.output.write_text(rendered+"\n",encoding="utf-8")
    print(rendered)
if __name__=="__main__": main()
