import hashlib, pathlib, sys, tempfile, unittest, struct
HERE=pathlib.Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/"tools" if (HERE.parent/"tools").is_dir() else HERE))
from build_pause_options_gold_row_v50 import build, BUTTON_NAME, ACTION_NAME, BUTTON_LABEL, STATEMENT
from hud_elements_codec_v42 import parse_hud
from hud_action_probe_v45 import parse_action_section

def s(value=b""):
    raw=value.encode("utf-8") if isinstance(value,str) else value
    return struct.pack("<I",len(raw))+raw
def f(value=0.0): return struct.pack("<f",value)
def common(name, typ, label="GameplayMenu"):
    out=bytearray(s(name)+bytes([typ])+s(label)+struct.pack("<I",0x80000001)+b"\x00")
    out+=f(1)+f(2)+f(1)+f(0.3)+f(0)+f(0)+bytes([255,0,0,0,201])+f(.05)
    out+=(bytes([255,127,127,127])*3)+s("JungleFever")+f(.465)+f(.069)+f(.382)+f(.12)+bytes([1,1])
    out+=s("")*4
    return bytes(out)
def synthetic_pause_hud():
    element=common("pickup_btn",2)+s("PICK UP: Normal")+f(.3)+f(-.16)+f(0)+bytes([0,0,0,0,0])+s("JungleFever")+s("")+s("onOptionPickUp")
    elements=struct.pack("<I",1)+element
    sections=[s("onOpen"),elements,b"\x00\x00",b"\x00\x00"]
    return struct.pack("<I",3)+b"NcP\x0c"+b"".join(struct.pack("<I",len(x))+x for x in sections)

class PauseOptionsGoldRowV50Tests(unittest.TestCase):
    def test_builds_one_button_on_existing_gameplay_tab(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td); source=root/"pause.hud"; output=root/"candidate.hud"
            original=synthetic_pause_hud(); source.write_bytes(original)
            result=build(source,output,allow_unpinned_source=True)
            self.assertEqual(hashlib.sha256(original).hexdigest(),result["source_sha256"])
            doc=parse_hud(output.read_bytes())
            button=next(e for e in doc["elements"] if e.field("name").value==BUTTON_NAME)
            self.assertEqual(button.field("label").value,"GameplayMenu")
            self.assertEqual(button.field("type2_string_140").value,BUTTON_LABEL)
            self.assertEqual(button.field("type2_string_178").value,ACTION_NAME)
            self.assertAlmostEqual(button.field("position_x").value,0.66,places=5)
            self.assertAlmostEqual(button.field("position_y").value,-0.7,places=5)
            action=parse_action_section(doc["sections"]["actions"])["actions"][0]
            self.assertEqual(action["name"],ACTION_NAME)
            self.assertEqual(action["statements"],[STATEMENT])
            self.assertEqual(len(doc["elements"]),2)
            self.assertFalse(result["runtime_verified"])
    def test_refuses_to_overwrite_source(self):
        with tempfile.TemporaryDirectory() as td:
            source=pathlib.Path(td)/"pause.hud"; source.write_bytes(synthetic_pause_hud())
            with self.assertRaisesRegex(ValueError,"refusing to overwrite source"):
                build(source,source,allow_unpinned_source=True)
    def test_refuses_existing_candidate(self):
        with tempfile.TemporaryDirectory() as td:
            root=pathlib.Path(td); source=root/"pause.hud"; output=root/"candidate.hud"
            source.write_bytes(synthetic_pause_hud()); output.write_bytes(b"existing")
            with self.assertRaisesRegex(FileExistsError,"refusing to overwrite"):
                build(source,output,allow_unpinned_source=True)
    def test_rejects_bad_source_hash_by_default(self):
        with tempfile.TemporaryDirectory() as td:
            source=pathlib.Path(td)/"pause.hud"; output=pathlib.Path(td)/"candidate.hud"
            source.write_bytes(synthetic_pause_hud())
            with self.assertRaisesRegex(ValueError,"source SHA-256 mismatch"):
                build(source,output)
    def test_source_fixture_has_expected_target_template(self):
        doc=parse_hud(synthetic_pause_hud())
        self.assertEqual(len(doc["elements"]),1)
        self.assertEqual(doc["elements"][0].field("name").value,"pickup_btn")
        self.assertEqual(doc["elements"][0].field("label").value,"GameplayMenu")

if __name__=="__main__": unittest.main(verbosity=2)
