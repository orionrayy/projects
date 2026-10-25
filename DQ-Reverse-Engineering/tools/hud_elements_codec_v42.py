#!/usr/bin/env python3
"""Field-preserving v12 HUD element codec. No game package is built or modified here."""
from __future__ import annotations
import argparse, json, pathlib, struct
from collections import Counter
from dataclasses import dataclass
from typing import Any

MARKERS = {b"NcP", b"NcX", b"NcI"}
SECTIONS = ("general", "elements", "actions", "timers")
MAX_STRING = 2_000_000
MAX_ELEMENTS = 100_000

class HudCodecError(ValueError):
    """Malformed, unsupported, or unsafe HUD serialization."""

@dataclass
class Field:
    name: str
    kind: str
    raw: bytes
    value: Any
    dirty: bool = False
    def encode(self) -> bytes:
        if not self.dirty:
            return self.raw
        if self.kind == "str":
            raw = str(self.value).encode("utf-8", errors="surrogateescape")
            if len(raw) > MAX_STRING: raise HudCodecError(f"string too large: {self.name}")
            return struct.pack("<I", len(raw)) + raw
        if self.kind == "u8":
            if not 0 <= int(self.value) <= 0xFF: raise HudCodecError(f"u8 out of range: {self.name}")
            return struct.pack("<B", int(self.value))
        if self.kind == "u16":
            if not 0 <= int(self.value) <= 0xFFFF: raise HudCodecError(f"u16 out of range: {self.name}")
            return struct.pack("<H", int(self.value))
        if self.kind == "u32":
            if not 0 <= int(self.value) <= 0xFFFFFFFF: raise HudCodecError(f"u32 out of range: {self.name}")
            return struct.pack("<I", int(self.value))
        if self.kind == "i16":
            if not -0x8000 <= int(self.value) <= 0x7FFF: raise HudCodecError(f"i16 out of range: {self.name}")
            return struct.pack("<h", int(self.value))
        if self.kind == "f32": return struct.pack("<f", float(self.value))
        if self.kind == "color":
            raw = bytes(self.value)
            if len(raw) != 4: raise HudCodecError(f"color must be four bytes: {self.name}")
            return raw
        raise HudCodecError(f"unsupported field kind: {self.kind}")

@dataclass
class Element:
    index: int
    element_type: int
    fields: list[Field]
    offset: int
    raw: bytes
    def field(self, name: str) -> Field:
        matches = [f for f in self.fields if f.name == name]
        if len(matches) != 1: raise HudCodecError(f"element[{self.index}] expected one {name!r}, found {len(matches)}")
        return matches[0]
    def set(self, name: str, value: Any) -> None:
        item = self.field(name)
        item.value, item.dirty = value, True
    def encode(self) -> bytes:
        return b"".join(field.encode() for field in self.fields)

class Reader:
    def __init__(self, data: bytes, label: str):
        self.data, self.label, self.pos = data, label, 0
    def read(self, n: int) -> bytes:
        if n < 0 or self.pos + n > len(self.data):
            raise HudCodecError(f"{self.label}: truncated at 0x{self.pos:x}; need {n}, have {len(self.data)-self.pos}")
        out = self.data[self.pos:self.pos+n]; self.pos += n; return out
    def field(self, name: str, kind: str) -> Field:
        if kind == "str":
            start = self.pos; length_raw = self.read(4); length = struct.unpack("<I", length_raw)[0]
            if length > MAX_STRING: raise HudCodecError(f"{self.label}: unreasonable string length {length} at 0x{start:x}")
            payload = self.read(length); raw = length_raw + payload
            value = payload.decode("utf-8", errors="surrogateescape")
        elif kind == "color":
            raw = self.read(4); value = list(raw)
        else:
            fmt = {"u8":"<B", "u16":"<H", "u32":"<I", "i16":"<h", "f32":"<f"}.get(kind)
            if fmt is None: raise HudCodecError(f"unsupported field kind: {kind}")
            raw = self.read(struct.calcsize(fmt)); value = struct.unpack(fmt, raw)[0]
        return Field(name, kind, raw, value)

def parse_element(data: bytes, offset: int, index: int) -> tuple[Element, int]:
    r = Reader(data[offset:], f"element[{index}]@0x{offset:x}")
    fields: list[Field] = []
    def add(name, kind): 
        item = r.field(name, kind); fields.append(item); return item.value
    try:
        add("name","str"); typ=add("type","u8"); add("label","str"); add("id_u32","u32")
        add("visible_flag","u8")
        for axis in "xy": add(f"position_{axis}","f32")
        for axis in "xy": add(f"size_{axis}","f32")
        add("scale_2c","f32"); add("aux_float_2c","f32")
        for i in range(5): add(f"common_flag_{i}","u8")
        add("scale_30","f32")
        for i in range(3): add(f"common_color_{i}","color")
        add("resource_40","str")
        for axis in "xy": add(f"vector_48_{axis}","f32")
        for axis in "xy": add(f"vector_50_{axis}","f32")
        add("common_flag_58","u8"); add("common_flag_59","u8")
        for i in range(4): add(f"common_string_{i}","str")
        if typ in (1,5,9,10,13): pass
        elif typ == 2:
            add("type2_string_140","str")
            for i in range(3): add(f"type2_float_{i}","f32")
            for i in range(5): add(f"type2_flag_{i}","u8")
            add("type2_resource_160","str"); add("type2_string_168","str"); add("type2_string_178","str")
        elif typ == 3:
            add("list_flag_1f4","u8")
            for i in range(3): add(f"list_float_a_{i}","f32")
            for i in range(3): add(f"list_flag_{i}","u8")
            for i in range(2): add(f"list_float_b_{i}","f32")
            add("list_resource_208","str"); add("list_string_210","str"); add("list_float_220","f32")
            for i in range(2): add(f"list_resource_pair_{i}","str")
            for i in range(7): add(f"list_color_{i}","color")
            for i in range(8): add(f"list_resource_tail_{i}","str")
            for i in range(2): add(f"list_float_tail_{i}","f32")
        elif typ == 4:
            add("type4_string_60","str")
            for i in range(3): add(f"type4_float_{i}","f32")
            for i in range(5): add(f"type4_flag_{i}","u8")
            add("type4_resource_88","str")
        elif typ == 6:
            add("type6_flag_c8","u8"); add("type6_string_90","str")
            for i in range(3): add(f"type6_float_{i}","f32")
            for i in range(5): add(f"type6_flag_{i}","u8")
            add("type6_resource_b0","str"); add("type6_string_b8","str")
        elif typ == 7: add("type7_resource","str")
        elif typ == 8:
            add("type8_flag_0","u8"); add("type8_flag_1","u8")
        elif typ == 11:
            add("type11_flag","u8")
            for i in range(3): add(f"type11_short_{i}","i16")
            add("type11_string_1a8","str"); add("type11_resource_1b8","str")
        elif typ in (12,14): add(f"type{typ}_resource","str")
        elif typ == 15:
            add("type15_flag_df","u8"); add("type15_string_e0","str")
            for i in range(3): add(f"type15_float_{i}","f32")
            for i in range(5): add(f"type15_flag_{i}","u8")
            for i in range(3): add(f"type15_resource_{i}","str")
            add("type15_resource_110","str"); add("type15_resource_118","str")
        else: raise HudCodecError(f"unknown element type {typ}")
    except (HudCodecError, struct.error) as exc:
        raise HudCodecError(f"element[{index}] at 0x{offset:x}, cursor 0x{offset+r.pos:x}: {exc}") from exc
    end = offset + r.pos
    return Element(index, typ, fields, offset, data[offset:end]), end

def parse_hud(data: bytes, source: str="<memory>") -> dict[str,Any]:
    if len(data) < 8: raise HudCodecError("short HUD header")
    marker_len = struct.unpack_from("<I",data,0)[0]; marker=data[4:7]; version=data[7]
    if marker_len != 3 or marker not in MARKERS: raise HudCodecError(f"invalid HUD marker/length: {marker_len}, {marker!r}")
    if version != 12: raise HudCodecError(f"only version 12 supported; got {version}")
    pos=8; sections={}
    for name in SECTIONS:
        if pos+4 > len(data): raise HudCodecError(f"truncated {name} section length")
        size=struct.unpack_from("<I",data,pos)[0]; pos+=4
        if pos+size > len(data): raise HudCodecError(f"truncated {name} section")
        sections[name]=data[pos:pos+size]; pos+=size
    if pos != len(data): raise HudCodecError(f"{len(data)-pos} trailing bytes after sections")
    general=Reader(sections["general"],"general section"); general.field("initial_action","str")
    if general.pos != len(sections["general"]): raise HudCodecError("unparsed general section bytes")
    elements_data=sections["elements"]
    if len(elements_data)<4: raise HudCodecError("element section missing count")
    count=struct.unpack_from("<I",elements_data,0)[0]
    if count>MAX_ELEMENTS: raise HudCodecError(f"unreasonable element count {count}")
    pos=4; elements=[]
    for index in range(count):
        element,pos=parse_element(elements_data,pos,index); elements.append(element)
    if pos != len(elements_data): raise HudCodecError(f"{len(elements_data)-pos} trailing bytes in element section")
    if len(sections["actions"])<2: raise HudCodecError("action section missing count")
    if len(sections["timers"])<2: raise HudCodecError("timer section missing count")
    return {"source":source,"data":data,"header":data[:8],"sections":sections,"elements":elements,
            "action_count":struct.unpack_from("<H",sections["actions"])[0],
            "timer_count":struct.unpack_from("<H",sections["timers"])[0]}

def encode_hud(document: dict[str,Any]) -> bytes:
    sections=dict(document["sections"])
    records=[]
    for i,element in enumerate(document["elements"]):
        if element.index != i: raise HudCodecError("element indices must remain dense and ordered")
        records.append(element.encode())
    sections["elements"]=struct.pack("<I",len(records))+b"".join(records)
    output=bytearray(document["header"])
    for name in SECTIONS:
        payload=sections[name]; output.extend(struct.pack("<I",len(payload))); output.extend(payload)
    rebuilt=bytes(output)
    checked=parse_hud(rebuilt,"<encoded>")
    if len(checked["elements"]) != len(document["elements"]): raise HudCodecError("element count changed on reparse")
    return rebuilt

def summary(document: dict[str,Any]) -> dict[str,Any]:
    types=Counter(e.element_type for e in document["elements"])
    return {"source":document["source"],"file_size":len(document["data"]),"element_count":len(document["elements"]),
            "element_type_counts":{str(k):v for k,v in sorted(types.items())},
            "action_count":document["action_count"],"timer_count":document["timer_count"]}

def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hud",type=pathlib.Path)
    parser.add_argument("--roundtrip",type=pathlib.Path,help="write unchanged reconstruction to a new file")
    parser.add_argument("--summary",action="store_true")
    args=parser.parse_args()
    document=parse_hud(args.hud.read_bytes(),str(args.hud)); rebuilt=encode_hud(document)
    if rebuilt != document["data"]: raise HudCodecError("no-op round-trip was not byte-identical")
    if args.roundtrip:
        dest=args.roundtrip.resolve()
        if dest==args.hud.resolve() or dest.exists(): raise HudCodecError("output must be a distinct, non-existing path")
        dest.parent.mkdir(parents=True,exist_ok=True); dest.write_bytes(rebuilt)
    result=summary(document);result.update({"noop_byte_identical":True,"writer":"field-preserving-v12","roundtrip_path":str(args.roundtrip) if args.roundtrip else None})
    print(json.dumps(result,indent=2,ensure_ascii=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
