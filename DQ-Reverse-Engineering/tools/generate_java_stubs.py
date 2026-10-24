#!/usr/bin/env python3
"""Emit declaration-only Java stubs from a locally extracted DEX using stdlib."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, struct

PRIM = {"V":"void","Z":"boolean","B":"byte","S":"short","C":"char","I":"int","J":"long","F":"float","D":"double"}
CLASS_FLAGS = {1:"public", 2:"private", 4:"protected", 16:"final", 512:"interface", 1024:"abstract", 2048:"synthetic", 8192:"annotation", 16384:"enum"}
FIELD_FLAGS = {1:"public",2:"private",4:"protected",8:"static",16:"final",64:"volatile",128:"transient",4096:"synthetic"}
METHOD_FLAGS = {1:"public",2:"private",4:"protected",8:"static",16:"final",32:"synchronized",64:"bridge",128:"varargs",256:"native",1024:"abstract",2048:"strictfp",4096:"synthetic"}

def uleb(b, p):
    value = shift = 0
    while True:
        if p >= len(b): raise ValueError("truncated ULEB128")
        n = b[p]; p += 1; value |= (n & 127) << shift
        if n < 128: return value, p
        shift += 7
        if shift > 35: raise ValueError("invalid ULEB128")

def jtype(d):
    if d.startswith("["): return jtype(d[1:]) + "[]"
    if d.startswith("L") and d.endswith(";"): return d[1:-1].replace("/", ".")
    return PRIM.get(d, d)

def modifiers(flags, mapping, allowed):
    return [name for bit, name in mapping.items() if flags & bit and name in allowed]

class Dex:
    def __init__(self, path):
        self.path = pathlib.Path(path); self.b = self.path.read_bytes(); b = self.b
        if len(b) < 112 or not b.startswith(b"dex\n"): raise ValueError("not a DEX file")
        self.u16 = lambda o: struct.unpack_from("<H", b, o)[0]
        self.u32 = lambda o: struct.unpack_from("<I", b, o)[0]
        self.strings = []
        for i in range(self.u32(56)):
            off = self.u32(self.u32(60) + 4*i); _, off = uleb(b, off)
            self.strings.append(b[off:b.index(b"\0", off)].decode("utf-8", "replace"))
        self.types = [self.strings[self.u32(self.u32(68)+4*i)] for i in range(self.u32(64))]
        self.protos = []
        for i in range(self.u32(72)):
            _, ret, par = struct.unpack_from("<III", b, self.u32(76)+12*i)
            args = []
            if par:
                n = self.u32(par); args = [self.types[self.u16(par+4+2*j)] for j in range(n)]
            self.protos.append((self.types[ret], args))
        self.fields = []
        for i in range(self.u32(80)):
            owner, typ, name = struct.unpack_from("<HHI", b, self.u32(84)+8*i)
            self.fields.append((self.types[owner], self.types[typ], self.strings[name]))
        self.methods = []
        for i in range(self.u32(88)):
            owner, proto, name = struct.unpack_from("<HHI", b, self.u32(92)+8*i)
            self.methods.append((self.types[owner], self.protos[proto], self.strings[name]))
        self.classes = []
        for i in range(self.u32(96)):
            ci, flags, sup, itf, src, ann, data, static = struct.unpack_from("<IIIIIIII", b, self.u32(100)+32*i)
            c = {"desc":self.types[ci],"flags":flags,"super":self.types[sup] if sup != 0xffffffff else None,"interfaces":[],"fields":[],"methods":[]}
            if itf:
                n = self.u32(itf); c["interfaces"] = [self.types[self.u16(itf+4+2*j)] for j in range(n)]
            if data:
                p = data; sf,p = uleb(b,p); inf,p = uleb(b,p); dm,p = uleb(b,p); vm,p = uleb(b,p)
                for count, kind in ((sf,"static"),(inf,"instance")):
                    idx = 0
                    for _ in range(count):
                        diff,p = uleb(b,p); af,p = uleb(b,p); idx += diff; c["fields"].append((idx,af,kind))
                for count, kind in ((dm,"direct"),(vm,"virtual")):
                    idx = 0
                    for _ in range(count):
                        diff,p = uleb(b,p); af,p = uleb(b,p); code,p = uleb(b,p); idx += diff
                        c["methods"].append((idx,af,code,kind))
            self.classes.append(c)

def java_identifier(s):
    keywords = {"abstract","assert","boolean","break","byte","case","catch","char","class","const","continue","default","do","double","else","enum","extends","final","finally","float","for","goto","if","implements","import","instanceof","int","interface","long","native","new","package","private","protected","public","return","short","static","strictfp","super","switch","synchronized","this","throw","throws","transient","try","void","volatile","while"}
    return s + "_" if s in keywords or not s else s

def render(dex, c):
    binary = c["desc"][1:-1]; pkg, sep, name = binary.rpartition("/")
    interfaces = bool(c["flags"] & 0x200); enum = bool(c["flags"] & 0x4000)
    kind = "interface" if interfaces else ("enum" if enum else "class")
    access = modifiers(c["flags"], CLASS_FLAGS, {"public","protected","private","abstract","final","strictfp"})
    head = " ".join(access + [kind, name])
    parents = []
    if c["super"] not in (None,"Ljava/lang/Object;") and not interfaces and not enum: parents.append("extends " + jtype(c["super"]))
    if c["interfaces"]: parents.append(("extends " if interfaces else "implements ") + ", ".join(jtype(x) for x in c["interfaces"]))
    if parents: head += " " + " ".join(parents)
    out = ["// GENERATED DECLARATION STUB; NOT ORIGINAL JAVA SOURCE.","// Nontrivial implementations are omitted; inspect the matching disassembly.",""]
    if sep: out += ["package " + pkg.replace("/","。").replace("。",".") + ";", ""]
    out += [head + " {"]
    for index, flags, kind_field in c["fields"]:
        owner, typ, field_name = dex.fields[index]
        mods = modifiers(flags, FIELD_FLAGS, {"public","protected","private","static","final","volatile","transient"})
        out.append("    " + (" ".join(mods)+" " if mods else "") + jtype(typ) + " " + java_identifier(field_name) + ";")
    if c["fields"]: out.append("")
    for idx, flags, code, meth_kind in c["methods"]:
        owner, (ret,args), name = dex.methods[idx]
        if name == "<clinit>":
            out += ["    static {", "        // Class initializer body is not reconstructed in this stub.", "    }"]
            continue
        mf = modifiers(flags, METHOD_FLAGS, {"public","protected","private","static","final","synchronized","native","abstract","strictfp"})
        is_ctor = name == "<init>"
        params = ", ".join(jtype(t) + " p" + str(i) for i,t in enumerate(args))
        sig = (name and name != "<init>" or False)
        sig = (binary.rsplit("/",1)[-1] if is_ctor else jtype(ret) + " " + java_identifier(name)) + "(" + params + ")"
        prefix = "    " + (" ".join(mf)+" " if mf else "")
        if flags & (0x100|0x400) or interfaces:
            out.append(prefix + sig + ";")
        else:
            out += [prefix + sig + " {"]
            if not is_ctor and ret != "V":
                out.append('        throw new UnsupportedOperationException("Stub only; see the Dalvik disassembly.");')
            else:
                out.append("        // Original method body intentionally not fabricated.")
            out.append("    }")
    out.append("}")
    return pathlib.Path(*binary.split("/")).with_suffix(".java"), "\n".join(out)+"\n"

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dex", type=pathlib.Path)
    ap.add_argument("--out", type=pathlib.Path, default=pathlib.Path("reconstruction/java"))
    ap.add_argument("--prefix", default="Lcom/shinybox/")
    args = ap.parse_args()
    dex = Dex(args.dex); emitted = []
    for c in dex.classes:
        if c["desc"].startswith(args.prefix):
            rel, source = render(dex, c); dst = args.out/rel; dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(source, encoding="utf-8"); emitted.append(str(dst))
    print(json.dumps({"input":str(args.dex),"sha256":hashlib.sha256(dex.b).hexdigest(),"counts":{"strings":dex.u32(56),"types":dex.u32(64),"prototypes":dex.u32(72),"fields":dex.u32(80),"methods":dex.u32(88),"classes":dex.u32(96)},"emitted":len(emitted),"output":str(args.out)},indent=2))
    print("WARNING: method implementations are intentionally not reconstructed.")
if __name__ == "__main__": main()
