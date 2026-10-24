#!/usr/bin/env python3
"""List class and method metadata in a Dalvik DEX file using stdlib only."""
from __future__ import annotations
import argparse, hashlib, json, pathlib, struct

class Dex:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.data = self.path.read_bytes()
        b = self.data
        if len(b) < 112 or not b.startswith(b"dex\n"):
            raise ValueError("input does not look like a DEX file")
        self.u16 = lambda o: struct.unpack_from("<H", b, o)[0]
        self.u32 = lambda o: struct.unpack_from("<I", b, o)[0]
        self.strings = []
        for i in range(self.u32(56)):
            off = self.u32(self.u32(60) + i * 4)
            _, p = self.uleb(off)
            end = b.index(b"\0", p)
            self.strings.append(b[p:end].decode("utf-8", "replace"))
        self.types = [self.strings[self.u32(self.u32(68) + i * 4)] for i in range(self.u32(64))]
        self.protos = []
        for i in range(self.u32(72)):
            shorty, ret, params = struct.unpack_from("<III", b, self.u32(76) + i * 12)
            args = []
            if params:
                n = self.u32(params)
                args = [self.types[self.u16(params + 4 + j * 2)] for j in range(n)]
            self.protos.append((self.types[ret], args))
        self.methods = []
        for i in range(self.u32(88)):
            cls, proto, name = struct.unpack_from("<HHI", b, self.u32(92) + i * 8)
            self.methods.append((self.types[cls], self.protos[proto], self.strings[name]))
        self.classes = []
        for i in range(self.u32(96)):
            cls, access, sup, interfaces, source, ann, data_off, static = struct.unpack_from("<IIIIIIII", b, self.u32(100) + i * 32)
            item = {"descriptor": self.types[cls], "access_flags": access,
                    "super": self.types[sup] if sup != 0xffffffff else None,
                    "source": self.strings[source] if source != 0xffffffff else None,
                    "methods": []}
            if data_off:
                p = data_off
                sf,p = self.uleb(p); inf,p = self.uleb(p)
                direct,p = self.uleb(p); virtual,p = self.uleb(p)
                for count, kind in ((sf,"static-field"), (inf,"instance-field")):
                    idx = 0
                    for _ in range(count):
                        diff,p = self.uleb(p); flags,p = self.uleb(p); idx += diff
                for count, kind in ((direct,"direct"), (virtual,"virtual")):
                    idx = 0
                    for _ in range(count):
                        diff,p = self.uleb(p); flags,p = self.uleb(p); code,p = self.uleb(p); idx += diff
                        owner, proto, name = self.methods[idx]
                        item["methods"].append({"name":name,"signature":self.sig(owner,proto,name),
                                                "access_flags":flags,"code_offset":code,"kind":kind})
            self.classes.append(item)
    def uleb(self, pos):
        out = shift = 0
        while True:
            value = self.data[pos]; pos += 1
            out |= (value & 0x7f) << shift
            if value < 0x80: return out, pos
            shift += 7
            if shift > 35: raise ValueError("invalid ULEB128")
    def java(self, desc):
        if desc.startswith("["): return self.java(desc[1:]) + "[]"
        if desc.startswith("L") and desc.endswith(";"): return desc[1:-1].replace("/",".")
        return {"V":"void","Z":"boolean","B":"byte","S":"short","C":"char","I":"int","J":"long","F":"float","D":"double"}.get(desc,desc)
    def sig(self, owner, proto, name):
        ret,args = proto
        return f"{self.java(ret)} {self.java(owner)}.{name}(" + ", ".join(self.java(a) for a in args) + ")"

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("dex", type=pathlib.Path)
    ap.add_argument("--prefix", default="Lcom/shinybox/", help="descriptor prefix to include")
    ap.add_argument("--output", type=pathlib.Path, default=pathlib.Path("dex-inventory.json"))
    args=ap.parse_args(); d=Dex(args.dex)
    selected=[c for c in d.classes if c["descriptor"].startswith(args.prefix)]
    report={"input":args.dex.name,"size_bytes":len(d.data),"sha256":hashlib.sha256(d.data).hexdigest(),
            "counts":{"strings":d.u32(56),"types":d.u32(64),"prototypes":d.u32(72),
                      "fields":d.u32(80),"method_ids":d.u32(88),"class_definitions":d.u32(96),
                      "included_classes":len(selected)},"classes":selected}
    args.output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps(report["counts"],indent=2))
    print("wrote",args.output)
if __name__=="__main__": main()
