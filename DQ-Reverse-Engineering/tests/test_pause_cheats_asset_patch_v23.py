import importlib.util, struct, unittest
from pathlib import Path

MOD_PATH=Path(__file__).resolve().parents[1]/"tools"/"patch_pause_cheats_sandbox_v23.py"
spec=importlib.util.spec_from_file_location("patch_v23",MOD_PATH)
mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)

def fixture(version=12,label=mod.OLD_LABEL,wrong_route=False,params_count=7):
    elems=struct.pack("<I",126)+mod.lp(label)+mod.lp(mod.CALLBACK)
    visibility=[f"<004><4,{i+1}>FakeGroup<3,1>{i%2}" for i in range(6)]
    route="not-the-audited-route" if wrong_route else mod.OLD_ROUTE
    params=visibility[:max(0,params_count-1)]+[route] if params_count else []
    actions=[
      {"name":"onResume","parameters":["<023>resume"],"extra_script":""},
      {"name":mod.CALLBACK,"parameters":params,"extra_script":""},
      {"name":"unrelated","parameters":["same"],"extra_script":"unchanged"}
    ]
    payload=bytearray(struct.pack("<H",len(actions)))
    for a in actions: payload+=mod.serialize_action(a,version)
    sections={"general_attributes":mod.lp("boot"),"elements":elems,
       "actions":bytes(payload),"timers":struct.pack("<H",0)}
    out=bytearray(struct.pack("<I",3)+b"NcP"+bytes([version]))
    for n in mod.SECTIONS: out+=struct.pack("<I",len(sections[n]))+sections[n]
    return bytes(out),actions

class V23PauseHudTests(unittest.TestCase):
    def test_preserves_callback_identity_signature_and_first_six_parameters(self):
        src,before=fixture()
        out,report=mod.patch_hud(src)
        sections,ver=mod.split_sections(out); after,raw=mod.parse_actions(sections["actions"],ver)
        self.assertEqual(len(before),3)
        self.assertEqual(len(after),3)
        target=after[1]
        self.assertEqual(target["name"],mod.CALLBACK)
        self.assertEqual(len(target["parameters"]),7)
        self.assertEqual(target["parameters"][:6],before[1]["parameters"][:6])
        self.assertEqual(target["parameters"][-1],mod.DEBUG_ROUTE)
        self.assertEqual(sections["elements"].count(mod.lp(mod.NEW_LABEL)),1)
        self.assertEqual(sections["elements"].count(mod.lp(mod.CALLBACK)),1)
        self.assertEqual(report["action_parameter_count_after"],7)
        self.assertTrue(report["unrelated_action_records_byte_identical"])

    def test_element_section_is_byte_count_preserving_and_other_actions_are_raw_identical(self):
        src,_=fixture()
        before,ver=mod.split_sections(src); _,raw0=mod.parse_actions(before["actions"],ver)
        out,_=mod.patch_hud(src)
        after,ver2=mod.split_sections(out); _,raw1=mod.parse_actions(after["actions"],ver2)
        self.assertEqual(len(before["elements"]),len(after["elements"]))
        self.assertEqual(before["general_attributes"],after["general_attributes"])
        self.assertEqual(before["timers"],after["timers"])
        self.assertEqual(raw0[0],raw1[0]); self.assertEqual(raw0[2],raw1[2])

    def test_fail_closed_on_wrong_schema_route_or_version(self):
        for kwargs in ({"version":11},{"wrong_route":True},{"params_count":6},{"label":"Other"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(mod.PatchError):
                mod.patch_hud(fixture(**kwargs)[0])

if __name__=="__main__": unittest.main(verbosity=2)
