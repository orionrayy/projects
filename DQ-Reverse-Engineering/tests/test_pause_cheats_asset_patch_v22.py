import importlib.util
import struct
import unittest
from pathlib import Path

MOD_PATH = Path(__file__).with_name('patch_pause_cheats_sandbox_v22.py')
spec = importlib.util.spec_from_file_location('pause_patch_v22', MOD_PATH)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fixture(version=12, label='Social/IAP', valid_schema=True):
    general = mod.lp('boot')
    elements = struct.pack('<I', 126) + mod.lp(label) + mod.lp('onShowSocial')
    params = ['p1','p2','p3','p4','p5','p6',
        '<023><8,3>013<2,14>uai_gp_options<2,9>onShowTab<1,5>3.000']
    if not valid_schema:
        params[-1] = 'different'
    actions = [
        {'name':'onResume','parameters':['resume-script'],'extra_script':''},
        {'name':'onShowSocial','parameters':params,'extra_script':''},
        {'name':'untouched','parameters':['keep-me'],'extra_script':'none'},
    ]
    payload = bytearray(struct.pack('<H',len(actions)))
    for action in actions:
        payload += mod.write_action(action, version)
    sections = {'general_attributes':general,'elements':elements,'actions':bytes(payload),'timers':struct.pack('<H',0)}
    result = bytearray(struct.pack('<I',3)+b'NcP'+bytes([version]))
    for name in mod.SECTIONS:
        result += struct.pack('<I',len(sections[name])) + sections[name]
    return bytes(result)

class PauseCheatsAssetPatchV22Tests(unittest.TestCase):
    def test_label_and_callback_keep_serialized_byte_length(self):
        self.assertEqual(len(mod.OLD_LABEL.encode()),len(mod.NEW_LABEL.encode()))
        self.assertEqual(len(mod.OLD_ACTION.encode()),len(mod.NEW_ACTION.encode()))
        source=fixture()
        patched,report=mod.patch_hud(source)
        before,_=mod.sections(source)
        after,version=mod.sections(patched)
        self.assertEqual(len(before['elements']),len(after['elements']))
        self.assertIn(mod.lp('Cheats/IAP'),after['elements'])
        self.assertIn(mod.lp('onShowCheats'),after['elements'])
        actions=mod.parse_actions(after['actions'],version)
        target=next(a for a in actions if a['name']=='onShowCheats')
        self.assertEqual(target['parameters'],[mod.RESUME,mod.DEBUG])
        self.assertEqual(len(actions),3)
        self.assertTrue(report['unrelated_actions_preserved'])

    def test_non_target_actions_and_sections_are_preserved(self):
        source=fixture()
        before,version=mod.sections(source)
        old=mod.parse_actions(before['actions'],version)
        patched,_=mod.patch_hud(source)
        after,version2=mod.sections(patched)
        new=mod.parse_actions(after['actions'],version2)
        self.assertEqual(before['general_attributes'],after['general_attributes'])
        self.assertEqual(before['timers'],after['timers'])
        for a,b in zip(old,new):
            if a['name']=='onShowSocial':
                self.assertEqual(b['name'],'onShowCheats')
            else:
                self.assertEqual(a,b)

    def test_wrong_version_and_unknown_schema_fail_closed(self):
        with self.assertRaises(mod.PatchError): mod.patch_hud(fixture(version=11))
        with self.assertRaises(mod.PatchError): mod.patch_hud(fixture(label='Other'))
        with self.assertRaises(mod.PatchError): mod.patch_hud(fixture(valid_schema=False))

if __name__=='__main__':
    unittest.main(verbosity=2)
