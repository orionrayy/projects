#!/usr/bin/env python3
"""Synthetic regression tests for the field-preserving v12 HUD codec."""
from __future__ import annotations
import struct, sys, unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from hud_elements_codec_v42 import HudCodecError, encode_hud, parse_hud

def s(value: bytes | str=b"") -> bytes:
    raw=value.encode("utf-8") if isinstance(value,str) else value
    return struct.pack("<I",len(raw))+raw
def f(value:float=0.0)->bytes:return struct.pack("<f",value)
def common(name:str,typ:int,label:bytes|str=b"label")->bytes:
    out=bytearray(s(name)+bytes([typ])+s(label)+struct.pack("<I",0x80000001)+b"\x01")
    out+=f(1)+f(2)+f(3)+f(4)+f(5)+f(6)+bytes([1,2,3,4,5])+f(7)
    out+=(bytes([255,1,2,3])*3)+s("resource")+f(8)+f(9)+f(10)+f(11)+bytes([1,1])
    out+=s("a")+s("b")+s("c")+s("d")
    return bytes(out)
def typed(typ:int)->bytes:
    if typ in (1,5,9,10,13):return b""
    if typ==2:return s("s140")+f(1)*3+bytes([1,2,3,4,5])+s("r160")+s("s168")+s("s178")
    if typ==3:return bytes([1])+f(1)*3+bytes([2,3,4])+f(5)*2+s("r208")+s("s210")+f(6)+s("r228")+s("r238")+(b"\x01\x02\x03\x04"*7)+b"".join(s(f"r{i}") for i in range(8))+f(7)*2
    if typ==4:return s("s60")+f(1)*3+bytes([1,2,3,4,5])+s("r88")
    if typ==6:return bytes([1])+s("s90")+f(1)*3+bytes([1,2,3,4,5])+s("rb0")+s("sb8")
    if typ==7:return s("resource")
    if typ==8:return bytes([1,2])
    if typ==11:return bytes([1])+struct.pack("<hhh",2,3,4)+s("s1a8")+s("r1b8")
    if typ in (12,14):return s("resource")
    if typ==15:return bytes([1])+s("se0")+f(1)*3+bytes([2,3,4,5,6])+s("r108")+s("s120")+s("s130")+s("r110")+s("r118")
    if typ==16:return b""  # malformed fixture used to verify fail-closed rejection
    raise AssertionError(typ)
def fixture(types:list[int],label:bytes|str=b"label")->bytes:
    el=struct.pack("<I",len(types))+b"".join(common(f"el{i}",t,label if i==0 else b"label")+typed(t) for i,t in enumerate(types))
    sections=(s("onOpen"),el,struct.pack("<H",0),struct.pack("<H",0))
    return struct.pack("<I",3)+b"NcP\x0c"+b"".join(struct.pack("<I",len(b))+b for b in sections)

class HudElementsCodecV42Tests(unittest.TestCase):
    def test_all_synthetic_element_types_roundtrip_byte_identically(self):
        original=fixture(list(range(1,16))); doc=parse_hud(original,"all-types.hud")
        self.assertEqual(len(doc["elements"]),15);self.assertEqual(encode_hud(doc),original)
    def test_label_edit_rebuilds_lengths_and_preserves_other_sections(self):
        original=fixture([1,2,3,4]);doc=parse_hud(original); old=dict(doc["sections"])
        doc["elements"][0].set("label","Cheat Menu / Sandbox — test")
        encoded=encode_hud(doc); reparsed=parse_hud(encoded)
        self.assertEqual(reparsed["elements"][0].field("label").value,"Cheat Menu / Sandbox — test")
        self.assertEqual(reparsed["elements"][1].raw,doc["elements"][1].raw)
        for key in ("general","actions","timers"):self.assertEqual(reparsed["sections"][key],old[key])
    def test_non_utf8_string_bytes_roundtrip(self):
        original=fixture([1],b"label\x93")
        self.assertEqual(encode_hud(parse_hud(original)),original)
    def test_unknown_type_truncation_wrong_version_and_trailing_data_rejected(self):
        with self.assertRaises(HudCodecError):parse_hud(fixture([16]))
        with self.assertRaises(HudCodecError):parse_hud(fixture([3])[:-1])
        bad=bytearray(fixture([1]));bad[7]=11
        with self.assertRaises(HudCodecError):parse_hud(bytes(bad))
        with self.assertRaises(HudCodecError):parse_hud(fixture([1])+b"x")
    def test_scalar_bounds_enforced(self):
        doc=parse_hud(fixture([1]));doc["elements"][0].set("visible_flag",999)
        with self.assertRaises(HudCodecError):encode_hud(doc)

if __name__=="__main__":unittest.main(verbosity=2)
