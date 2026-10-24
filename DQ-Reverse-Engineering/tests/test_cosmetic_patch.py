import pathlib, tempfile, unittest, xml.etree.ElementTree as ET, sys
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from apply_cosmetic_earnability_patch import apply_patch

class CosmeticPatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=pathlib.Path(self.tmp.name)
        (self.root/"src/Resources/XML").mkdir(parents=True)
        (self.root/"src/Resources/XML/Vanity.xml").write_text(
            '<Vanity><Row><Name>Wings</Name><Price>2.99</Price><Gold /></Row>'
            '<Row><Name>Conflict</Name><Price>1.99</Price><Gold>100</Gold></Row>'
            '<Row><Name>Unknown</Name><Price>9.99</Price><Gold /></Row>'
            '<Row><Name>AlreadyFree</Name><Price /><Gold>5000</Gold></Row></Vanity>',encoding="utf-8")
        (self.root/"src/Resources/XML/Other.xml").write_text("<Other/>",encoding="utf-8")
    def tearDown(self): self.tmp.cleanup()
    def test_cash_only_row_converted(self):
        report=apply_patch(self.root/"src",self.root/"out")
        root=ET.parse(self.root/"out/Resources/XML/Vanity.xml").getroot()
        rows={r.findtext("Name"):r for r in root.findall("Row")}
        self.assertEqual(rows["Wings"].findtext("Gold"),"750000")
        self.assertIn(rows["Wings"].findtext("Price"),(None,""))
        self.assertEqual(report["converted_count"],1)
    def test_existing_gold_conflict_not_changed(self):
        report=apply_patch(self.root/"src",self.root/"out")
        row=[r for r in ET.parse(self.root/"out/Resources/XML/Vanity.xml").getroot().findall("Row") if r.findtext("Name")=="Conflict"][0]
        self.assertEqual(row.findtext("Gold"),"100")
        self.assertEqual(len(report["conflicts"]),1)
    def test_unknown_price_reported(self):
        report=apply_patch(self.root/"src",self.root/"out")
        self.assertEqual(len(report["unresolved"]),1)
    def test_output_overlap_rejected(self):
        with self.assertRaises(ValueError): apply_patch(self.root/"src",self.root/"src/out")
    def test_existing_output_rejected(self):
        (self.root/"out").mkdir()
        with self.assertRaises(ValueError): apply_patch(self.root/"src",self.root/"out")
if __name__=="__main__": unittest.main()
