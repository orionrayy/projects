import pathlib, tempfile, unittest, xml.etree.ElementTree as ET, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apply_fair_economy_data_patch import apply_patch

class FairEconomyPatchTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        src = self.root / "src"
        (src / "Resources/XML").mkdir(parents=True)
        (src / "Resources/XML/IAP.xml").write_text(
            '<IAP><Schema><Name>String</Name></Schema><Row id="1"><Name>vanity1</Name></Row>'
            '<Row id="2"><Name>vanity72</Name></Row><Row id="3"><Name>vanity73</Name></Row>'
            '<Row id="4"><Name>vanity9</Name></Row></IAP>', encoding="utf-8")
        (src / "Resources/XML/Vanity.xml").write_text(
            '<Vanity><Schema><Name>String</Name><Price>Number</Price><Gold>Number</Gold></Schema>'
            '<Row id="1"><Name>Angel</Name><Price>2.99</Price><Gold /></Row>'
            '<Row id="9"><Name>Other</Name><Price /><Gold>100000</Gold></Row>'
            '<Row id="72"><Name>Spooky Jack Skin</Name><Price /><Gold /></Row>'
            '<Row id="73"><Name>Creepy Eye Skin</Name><Price /><Gold /></Row>'
            '<Row id="50"><Name>Unused</Name><Price /><Gold /></Row></Vanity>', encoding="utf-8")
        (src / "Resources/XML/Shop.xml").write_text(
            '<Shop><Schema><Tab1>Number</Tab1><Tab2>Number</Tab2><Tab3>Number</Tab3></Schema>'
            '<Row id="1"><Tab1 /><Tab2 /><Tab3>1</Tab3></Row></Shop>', encoding="utf-8")
        self.src, self.out = src, self.root / "out"
    def tearDown(self): self.tmp.cleanup()
    def test_cash_item_converts(self):
        r = apply_patch(self.src, self.out)
        row = next(x for x in ET.parse(self.out / "Resources/XML/Vanity.xml").getroot().findall("Row") if x.get("id") == "1")
        self.assertEqual(row.findtext("Gold"), "750000")
        self.assertIn(row.findtext("Price"), (None, ""))
        self.assertEqual(r["converted_cash_count"], 1)
    def test_unpriced_iap_items_get_gold_and_shop_entries(self):
        r = apply_patch(self.src, self.out)
        v = ET.parse(self.out / "Resources/XML/Vanity.xml").getroot()
        gold = {x.get("id"): x.findtext("Gold") for x in v.findall("Row")}
        self.assertEqual(gold["72"], "500000")
        self.assertEqual(gold["73"], "250000")
        s = ET.parse(self.out / "Resources/XML/Shop.xml").getroot()
        refs = [x.findtext("Tab3") for x in s.findall("Row")]
        self.assertIn("72", refs); self.assertIn("73", refs)
        self.assertEqual(r["shop_rows_after"], 3)
    def test_existing_gold_preserved(self):
        apply_patch(self.src, self.out)
        row = next(x for x in ET.parse(self.out / "Resources/XML/Vanity.xml").getroot().findall("Row") if x.get("id") == "9")
        self.assertEqual(row.findtext("Gold"), "100000")
    def test_iap_xml_untouched(self):
        before = (self.src / "Resources/XML/IAP.xml").read_bytes()
        apply_patch(self.src, self.out)
        self.assertEqual((self.out / "Resources/XML/IAP.xml").read_bytes(), before)
    def test_unknown_unpriced_sku_is_left_untouched_and_reported(self):
        p = self.src / "Resources/XML/IAP.xml"
        p.write_text(p.read_text().replace("</IAP>", '<Row id="5"><Name>vanity50</Name></Row></IAP>'))
        report = apply_patch(self.src, self.out)
        self.assertTrue(any(x.get("sku") == "vanity50" for x in report["manual_review"]))
        row = next(x for x in ET.parse(self.out / "Resources/XML/Vanity.xml").getroot().findall("Row") if x.get("id") == "50")
        self.assertIn(row.findtext("Gold"), (None, ""))
        self.assertTrue(report["remaining_iap_vanity_without_gold"])
    def test_output_directory_must_not_exist(self):
        self.out.mkdir()
        with self.assertRaisesRegex(ValueError, "exists; refusing"):
            apply_patch(self.src, self.out)

if __name__ == "__main__":
    unittest.main()
