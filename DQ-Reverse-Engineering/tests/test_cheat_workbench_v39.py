import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
HTML=ROOT/"cheats-sandbox"/"cheats_options_workbench_v39.html"
CATALOG=ROOT/"cheats-sandbox"/"debug_cheats_catalog_v39.json"
MATRIX=ROOT/"docs"/"CHEAT_CATALOG_IMPLEMENTATION_MATRIX_V39.json"
VALIDATOR=ROOT/"tools"/"validate_cheat_workbench_v39.py"

class V39WorkbenchTests(unittest.TestCase):
    def validate(self,html=HTML,catalog=CATALOG,matrix=MATRIX):
        return subprocess.run([sys.executable,str(VALIDATOR),"--html",str(html),"--catalog",str(catalog),"--matrix",str(matrix)],capture_output=True,text=True,check=False)
    def test_real_artifacts_validate(self):
        r=self.validate()
        self.assertEqual(r.returncode,0,r.stdout+r.stderr)
        self.assertIn("222 entries, 14 categories",r.stdout)
    def test_catalog_has_222_unique_stable_ids_and_14_categories(self):
        c=json.loads(CATALOG.read_text())
        self.assertEqual(len(c["cheats"]),222)
        self.assertEqual(len({x["id"] for x in c["cheats"]}),222)
        self.assertEqual(len(c["categories"]),14)
    def test_all_catalog_entries_are_blocked_until_adapter_exists(self):
        c=json.loads(CATALOG.read_text())
        self.assertTrue(all(x["integration_status"]=="requires_game_adapter" for x in c["cheats"]))
    def test_matrix_has_zero_runtime_verified_claims(self):
        m=json.loads(MATRIX.read_text())
        self.assertEqual(m["counts_by_game_status"]["runtime_verified"],0)
        self.assertFalse(any(x["runtime_verified"] for x in m["entries"]))
    def test_validator_rejects_document_scroll_instead_of_internal_list(self):
        good=HTML.read_text()
        bad=good.replace(".cheat-scroll{flex:1 1 auto;min-height:100px;min-width:0;overflow-y:auto", ".cheat-scroll{flex:1 1 auto;min-height:100px;min-width:0;overflow-y:visible",1)
        with tempfile.TemporaryDirectory() as td:
            temp=Path(td)/"bad.html";temp.write_text(bad)
            r=self.validate(html=temp)
            self.assertNotEqual(r.returncode,0)
            self.assertIn("own vertical scroll container",r.stdout)
if __name__=="__main__":
    unittest.main()
